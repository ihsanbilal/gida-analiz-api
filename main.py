import os
from fastapi import FastAPI, UploadFile, File
import google.generativeai as genai
from PIL import Image
import io
import json

app = FastAPI()

# Kendi API Anahtarını kullanmaya devam et
YOUR_API_KEY = "AIzaSyBGeY9SpEOk9-QXenYxOqSUWCs-nkCclfA"
genai.configure(api_key=YOUR_API_KEY)

# Gemini 3 Flash Preview modelini tanımlıyoruz
model = genai.GenerativeModel('gemini-3-flash-preview')

@app.post("/analiz-et")
async def analiz_et(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        prompt = """
        Sen uzman bir Gıda Mühendisisin. Görevin, resimdeki ürünü OpenFoodFacts 'Nutri-Score' (A, B, C, D, E) 
        ve Türk Gıda Kodeksi standartlarına göre analiz etmektir.

        ANALİZ KRİTERLERİ:
        - Pozitif: Meyve/Sebze/Baklagil oranı, Lif, Protein.
        - Negatif: Enerji (kalori), Doymuş Yağ, Şeker, Sodyum (Tuz).
        - Katkı Maddeleri: NBŞ, MSG, Trans Yağ, Nitrit/Nitrat, Yapay Renklendiriciler.

        YANIT FORMATI (KESİNLİKLE SADECE JSON):
        {
          "harf_notu": "[A-E arası bir harf]",
          "skor": [0-100 arası sayısal sağlık puanı],
          "analiz": "### 📦 [Kategori]\\n\\n**📊 Nutri-Score Özeti:** [Neden bu harfi aldığını açıkla]\\n\\n**⚠️ Riskli İçerikler:**\\n- [Madde]: [Açıklama]\\n\\n**🥛 Alerjenler:** [Varsa]\\n\\n**✅ Olumlu Yönler:** [Yüksek lif, protein vb.]"
        }
        """
        
        response = model.generate_content([prompt, image])
        res_text = response.text.strip()
        
        # JSON Temizleme
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0].strip()
        elif "```" in res_text:
            res_text = res_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(res_text)

    except Exception as e:
        print(f"HATA: {str(e)}")
        return {"harf_notu": "E", "skor": 0, "analiz": f"Hata: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)