![](LongBench/misc/logo.gif)
# 📚 LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks
<p align="center">
    🌐 <a href="https://longbench2.github.io" target="_blank">Project Page</a> • 📚 <a href="https://arxiv.org/abs/2412.15204" target="_blank">LongBench v2 Paper</a> • 📊 <a href="https://huggingface.co/datasets/THUDM/LongBench-v2" target="_blank">LongBench v2 Dataset</a> • 𝕏 <a href="https://x.com/realYushiBai/status/1869946577349132766" target="_blank">Thread</a>
</p>
<p align="center">
    📖 <a href="https://arxiv.org/abs/2308.14508" target="_blank">LongBench Paper</a> • 🤗 <a href="https://huggingface.co/datasets/THUDM/LongBench" target="_blank">LongBench Dataset</a>
</p>

**📢 The original LongBench v1 related files are moved under `LongBench/`, read its README [here](LongBench/README.md)**.

---

## 📌 Proje Açıklaması
Bu betik, **LongBench** veri kümesi üzerinde çeşitli LLM modelleri kullanarak tahminler çalıştırmak için geliştirilmiştir. OpenAI, Hugging Face ve Gemini modellerini destekler. Ayrıca, bu repoyu fork ederek geliştirdim: [Forklanan Repo](https://github.com/iclal07/LongBenchv2)

---

## ⚙️ Kurulum Adımları

### Gerekli Bağımlılıkları Yükleyin
```sh
pip install -r requirements.txt
```

### API Anahtarlarını Ayarlayın
`.env` dosyanızı oluşturun ve aşağıdaki değişkenleri tanımlayın:
```env
API_KEY=your_openai_key
GEMINI_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
```

---

## 🚀 Kullanım Talimatları

### Temel Kullanım
```sh
python pred.py --model gpt-4 --save_dir results
```

### Özel API URL'si Kullanımı
```sh
python pred.py --model qwen --base_url http://custom-url.com/v1
```

📌 **Not:** Eğer `--base_url` girilmezse **varsayılan olarak** `http://localhost:8000/v1` kullanılacaktır.

---

## 🔧 Parametre Açıklamaları

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `--base_url` | Kullanılacak API adresi | `http://localhost:8000/v1` |
| `--model` | Kullanılacak modelin ismi (`gpt-4`, `qwen`, `gemini-2.0-flash-exp` vb.) | `GLM-4-9B-Chat` |
| `--save_dir` | Sonuçların kaydedileceği dizin | `results` |
| `--cot` | Chain of Thought (COT) açmak için flag | `False` |
| `--no_context` | Modelin bağlam kullanmadan çalışmasını sağlamak için flag | `False` |
| `--rag` | Kaç tane bağlamsal veri kullanılacağını belirtir | `0` |

---

## 📁 Çıktılar

- Tahminler `.jsonl` formatında `save_dir` klasörüne kaydedilir.
- Çıktı örneği:
  ```json
  {
    "_id": "123",
    "question": "What is AI?",
    "response": "AI stands for Artificial Intelligence.",
    "pred": "B",
    "judge": true
  }
  ```

---

## 🔬 Deneysel Analizler
Bu çalışmada **Gemini2.0 Flash Experimental** ve **Qwen2.5-14B-Instruct-1M** modellerini kullandım ve iki farklı ayar altında sonuçları karşılaştırdım:

### Sonuçlar:
1. **CoT olmadan yapılan deney:**
   ![CoT Olmadan](exp-wo-cot.png)
2. **CoT ile yapılan deney:**
   ![CoT ile](exp-cot.png)

---

## 🛠️ Hata Giderme ve Loglama
- **Hata Yönetimi:** API çağrılarında hata olursa, 5 defaya kadar tekrar denenir.
- **Gecikme Mekanizması:** Gemini ve diğer modeller için **1-3 saniyelik rastgele bekleme süresi** eklendi.
- **Hata mesajları** konsola yazdırılır ve 1 saniye beklenerek tekrar denenir.

---

## 📜 Lisans
MIT Lisansı


🔗 **Herhangi bir sorun yaşarsanız, issue açabilirsiniz!** 🚀
