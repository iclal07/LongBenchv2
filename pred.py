import os, json, time, argparse, re, random
import torch.multiprocessing as mp
from tqdm import tqdm
from datasets import load_dataset
from transformers import AutoTokenizer
from openai import OpenAI
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

# API Anahtarları
HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
API_KEY = os.getenv("API_KEY")

# Model yapılandırmaları
model_map = json.loads(open('config/model2path.json', encoding='utf-8').read())
maxlen_map = json.loads(open('config/model2maxlen.json', encoding='utf-8').read())

# Prompt şablonları
template_rag = open('prompts/0shot_rag.txt', encoding='utf-8').read()
template_no_context = open('prompts/0shot_no_context.txt', encoding='utf-8').read()
template_0shot = open('prompts/0shot.txt', encoding='utf-8').read()
template_0shot_cot = open('prompts/0shot_cot.txt', encoding='utf-8').read()
template_0shot_cot_ans = open('prompts/0shot_cot_ans.txt', encoding='utf-8').read()

def query_llm(prompt, model, base_url, client=None, temperature=0.5, max_new_tokens=128):
    """ Farklı modeller için uygun API çağrısını yapar."""
    
    if "gemini" in model:
        client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = "gemini-2.0-flash-exp"
    else:
        client = OpenAI(
            base_url=base_url,
            api_key=API_KEY
        )
        model = model_map.get(model, model)
    
    tries = 0
    while tries < 5:
        tries += 1
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_new_tokens,
            )
            time.sleep(random.uniform(1, 3))
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Hata oluştu: {str(e)} - Tekrar deneniyor...")
            time.sleep(1)
    return ''

def extract_answer(response):
    """ Model cevabından doğru şıkkı çıkarır."""
    response = response.replace('*', '')
    match = re.search(r'The correct answer is \(([A-D])\)', response)
    if match:
        return match.group(1)
    else:
        match = re.search(r'The correct answer is ([A-D])', response)
        return match.group(1) if match else None

def get_pred(data, args, fout):
    """ Verileri işleyerek tahminleri alır."""
    for item in tqdm(data):
        context = item['context']
        if args.rag > 0:
            template = template_rag
            retrieved = sorted(item["retrieved_context"][:args.rag], key=lambda x: x['c_idx'])
            context = '\n\n'.join([f"Retrieved chunk {idx+1}: {x['content']}" for idx, x in enumerate(retrieved)])
        elif args.no_context:
            template = template_no_context
        elif args.cot:
            template = template_0shot_cot
        else:
            template = template_0shot
        
        prompt = template.replace('$DOC$', context.strip()).replace('$Q$', item['question'].strip())\
            .replace('$C_A$', item['choice_A'].strip()).replace('$C_B$', item['choice_B'].strip())\
            .replace('$C_C$', item['choice_C'].strip()).replace('$C_D$', item['choice_D'].strip())
        
        time.sleep(random.uniform(1, 3))
        output = query_llm(prompt, args.model, args.base_url, temperature=0.1, max_new_tokens=512 if args.cot else 128)
        if output == '':
            continue
        
        item['response'] = output.strip()
        item['pred'] = extract_answer(output)
        item['judge'] = item['pred'] == item['answer']
        item['context'] = context[:1000]
        fout.write(json.dumps(item, ensure_ascii=False) + '\n')
        fout.flush()

def main():
    os.makedirs(args.save_dir, exist_ok=True)
    print(args)
    out_file = os.path.join(args.save_dir, args.model.split("/")[-1] + ".jsonl")
    
    dataset = load_dataset('THUDM/LongBench-v2', split='train')
    data_all = [{"_id": item["_id"], "question": item["question"], "context": item["context"],
                 "choice_A": item["choice_A"], "choice_B": item["choice_B"], "choice_C": item["choice_C"],
                 "choice_D": item["choice_D"], "answer": item["answer"]} for item in dataset]
    
    has_data = {}
    if os.path.exists(out_file):
        with open(out_file, encoding='utf-8') as f:
            has_data = {json.loads(line)["_id"]: 0 for line in f}
    
    fout = open(out_file, 'a', encoding='utf-8')
    data = [item for item in data_all if item["_id"] not in has_data]
    
    data_subsets = [data[i::args.n_proc] for i in range(args.n_proc)]
    processes = []
    for rank in range(args.n_proc):
        p = mp.Process(target=get_pred, args=(data_subsets[rank], args, fout))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    fout.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_dir", "-s", type=str, default="results")
    parser.add_argument("--model", "-m", type=str, default="GLM-4-9B-Chat")
    parser.add_argument("--base_url", "-b", type=str, default="http://localhost:8000/v1")
    parser.add_argument("--cot", "-cot", action='store_true')
    parser.add_argument("--no_context", "-nc", action='store_true')
    parser.add_argument("--rag", "-rag", type=int, default=0)
    parser.add_argument("--n_proc", "-n", type=int, default=16)
    args = parser.parse_args()
    main()
