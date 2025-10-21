# promptlab_model.py 
import pandas as pd
import numpy as np
import json
import re
import os
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import chromadb

print("🎯 PROMPTLAB FINAL - Gemini RAG Sistemi yükleniyor...")

# Gemini API - opsiyonel
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Gemini API kütüphanesi bulundu")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini API yüklü değil")

# ==================== VECTOR STORE ====================
class VectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.documents = []
        self.metadatas = []
        
        try:
            self.client = chromadb.EphemeralClient()
            self.collection = self.client.create_collection("prompt_examples")
        except:
            self.collection = None
    
    def add_prompts(self, prompts_data):
        self.documents = []
        self.metadatas = []
        ids = []
        
        for i, prompt_info in enumerate(prompts_data):
            self.documents.append(prompt_info['prompt'])
            self.metadatas.append({
                'act': prompt_info.get('act', 'general'),
                'type': prompt_info.get('type', 'general')
            })
            ids.append(str(i))
        
        try:
            if self.collection:
                self.collection.add(
                    documents=self.documents,
                    metadatas=self.metadatas,
                    ids=ids
                )
        except:
            pass
        
        if self.documents:
            try:
                self.vectorizer.fit(self.documents)
            except:
                pass
    
    def search_similar_prompts(self, query: str, n_results: int = 3):
        try:
            if self.collection and self.documents:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(n_results, len(self.documents))
                )
                return results
        except:
            pass
        
        # TF-IDF fallback
        try:
            if self.documents and hasattr(self.vectorizer, 'vocabulary_'):
                query_vec = self.vectorizer.transform([query])
                doc_vecs = self.vectorizer.transform(self.documents)
                similarities = cosine_similarity(query_vec, doc_vecs).flatten()
                
                top_indices = similarities.argsort()[-n_results:][::-1]
                return {
                    'documents': [[self.documents[i] for i in top_indices]],
                    'metadatas': [[self.metadatas[i] for i in top_indices]],
                    'distances': [[1 - similarities[i] for i in top_indices]]
                }
        except:
            pass
        
        return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

# ==================== GEMINI RAG AGENT ====================
class GeminiRAGAgent:
    def __init__(self, api_key: str = None):
        self.available = False
        self.model = None
        
        if not GEMINI_AVAILABLE:
            return
        
        api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.available = True
            print("✅ Gemini RAG Agent hazır!")
        except Exception as e:
            print(f"❌ Gemini hatası: {e}")
            self.available = False
    
    def generate_optimized_prompt(self, user_prompt: str, similar_examples: List[str], context: Dict) -> str:
        if not self.available:
            return None
        
        rag_prompt = self._build_rag_prompt(user_prompt, similar_examples, context)
        
        try:
            response = self.model.generate_content(
                rag_prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_output_tokens': 1024,
                }
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini generation hatası: {e}")
            return None
    
    def _build_rag_prompt(self, user_prompt: str, similar_examples: List[str], context: Dict) -> str:
        examples_text = "\n\n".join([
            f"Örnek {i+1}:\n{example}"
            for i, example in enumerate(similar_examples[:3])
        ])
        
        category = context.get('category', 'genel')
        intent = context.get('intent', 'genel')
        
        return f"""Sen bir prompt optimizasyon uzmanısın. Görevin kullanıcının basit prompt'unu, profesyonel ve etkili bir prompt'a dönüştürmek.

KULLANICI PROMPT'U:
"{user_prompt}"

PROMPT ANALİZİ:
- Kategori: {category}
- Amaç: {intent}

BENZER BAŞARILI PROMPT ÖRNEKLERİ:
{examples_text}

GÖREV:
Yukarıdaki başarılı örnekleri referans alarak, kullanıcının prompt'unu optimize et.

KURALLAR:
1. Orijinal prompt'un amacını koru
2. Benzer örneklerdeki yapıyı ve stili uygula
3. Net, detaylı ve actionable bir prompt yaz
4. Türkçe kullan (orijinal Türkçe ise)
5. Uzun açıklamalar yapma, direkt optimize edilmiş prompt'u ver

OPTİMİZE EDİLMİŞ PROMPT:"""

# ==================== PROMPT ANALYZER ====================
class PromptAnalyzer:
    def analyze_prompt(self, prompt: str) -> Dict:
        word_count = len(prompt.split())
        
        return {
            'length_score': 0.4 if word_count < 10 else 0.7,
            'specificity_score': 0.3,
            'overall_score': 0.4,
            'issues': ['Çok kısa', 'Detay eksik'] if word_count < 10 else [],
            'word_count': word_count,
            'category': self._detect_category(prompt),
            'intent': self._detect_intent(prompt)
        }
    
    def _detect_intent(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ['öğret', 'nasıl', 'anlat', 'açıkla']):
            return 'teaching'
        elif any(kw in prompt_lower for kw in ['sen bir', 'rolünde']):
            return 'role_play'
        elif any(kw in prompt_lower for kw in ['kod yaz', 'program']):
            return 'code_generation'
        elif any(kw in prompt_lower for kw in ['yaz', 'oluştur']):
            return 'content_creation'
        
        return 'general'
    
    def _detect_category(self, prompt: str) -> str:
        intent = self._detect_intent(prompt)
        
        if intent == 'teaching':
            return 'öğretim'
        elif intent == 'role_play':
            return 'rol oynama'
        elif intent == 'code_generation':
            return 'kod yazma'
        elif intent == 'content_creation':
            return 'içerik oluşturma'
        
        return 'genel'

# ==================== FALLBACK OPTIMIZER ====================
class FallbackOptimizer:
    def optimize_prompt(self, original: str, similar_examples: List[str], context: Dict) -> str:
        topic = self._extract_topic(original)
        intent = context.get('intent', 'general')
        
        if similar_examples:
            template = similar_examples[0]
            if 'Sen bir' in template:
                return f"Sen bir {topic} uzmanısın. {template.split('.', 1)[1] if '.' in template else 'Kullanıcıya yardımcı ol.'}"
        
        if intent == 'teaching':
            return f"Sen bir {topic} öğretmenisin. Kullanıcıya {topic} konusunu adım adım öğret. Örnekler ver, pratik alıştırmalar sun."
        else:
            return f"{topic.capitalize()} hakkında detaylı ve kapsamlı bir yanıt ver. Örnekler kullan, net açıklamalar yap."
    
    def _extract_topic(self, prompt: str) -> str:
        stop_words = ['sen', 'bir', 'bana', 'hakkında', 'yaz', 'öğret']
        words = [w for w in prompt.split() if w.lower() not in stop_words and len(w) > 2]
        return ' '.join(words[:2]) if words else 'konu'

# ==================== ANA RAG PIPELINE ====================
class GeminiPromptLabRAG:
    def __init__(self, gemini_api_key: str = None):
        print("🎯 PromptLab RAG Pipeline başlatılıyor...")
        
        self.analyzer = PromptAnalyzer()
        self.vector_store = VectorStore()
        self.gemini_agent = GeminiRAGAgent(gemini_api_key)
        self.fallback_optimizer = FallbackOptimizer()
        
        self._load_dataset()
        
        mode = "Gemini RAG" if self.gemini_agent.available else "Fallback"
        print(f"✅ PROMPTLAB HAZIR! (Mod: {mode})")
    
    def _load_dataset(self):
        dataset = [
            {
                "act": "Python Teacher",
                "prompt": "Sen bir Python öğretmenisin. Öğrencilere Python'ı adım adım öğret. Temel syntax'tan başla, her kavramı örneklerle açıkla, kod alıştırmaları ver. Sabırlı, net ve teşvik edici ol.",
                "type": "teaching"
            },
            {
                "act": "Code Reviewer",
                "prompt": "Sen bir senior developer'sın. Kodu incele: okunabilirlik, performans, güvenlik, best practices. Yapıcı geri bildirim ver, alternatif çözümler öner.",
                "type": "coding"
            },
            {
                "act": "Academic Writer",
                "prompt": "Sen bir akademik yazarsın. Yapı: Giriş (bağlam, tez), Gelişme (argümanlar, kanıtlar), Sonuç (özet, çıkarımlar). Formal dil, kaynak göster, objektif ol.",
                "type": "writing"
            },
            {
                "act": "Math Teacher",
                "prompt": "Sen bir matematik öğretmenisin. Konsepti açıkla, adım adım çöz, alternatif yöntemler göster, pratik problemler ver. Görsel yardımcılar kullan.",
                "type": "teaching"
            },
            {
                "act": "Business Analyst",
                "prompt": "Sen bir iş analistisin. Veri analizi yap, KPI'lar tanımla, insights sun, iyileştirme önerileri getir. SWOT, market research kullan.",
                "type": "business"
            },
            {
                "act": "Content Writer",
                "prompt": "Sen bir içerik yazarısın. SEO-friendly, engaging içerik yaz. Net başlıklar, değer kat, hedef kitleye uygun ton, CTA ekle.",
                "type": "writing"
            },
            {
                "act": "UX Designer",
                "prompt": "Sen bir UX tasarımcısısın. User-centered design yap, wireframes oluştur, usability test et. Accessibility standartlarına uy.",
                "type": "design"
            },
            {
                "act": "Data Scientist",
                "prompt": "Sen bir veri bilimcisin. Veri analizi yap, ML modelleri oluştur, istatistiksel analiz gerçekleştir. Python kullan, görselleştir.",
                "type": "data"
            }
        ]
        
        self.vector_store.add_prompts(dataset)
    
    def process_prompt(self, user_prompt: str) -> Dict:
        """Ana RAG işlemi - HER ZAMAN rag_mode döndürür"""
        
        # 1. ANALYZE
        analysis = self.analyzer.analyze_prompt(user_prompt)
        
        # 2. RETRIEVE
        similar_prompts = self.vector_store.search_similar_prompts(user_prompt, n_results=3)
        similar_examples = similar_prompts['documents'][0] if similar_prompts['documents'][0] else []
        
        # 3. GENERATE
        if self.gemini_agent.available:
            optimized = self.gemini_agent.generate_optimized_prompt(
                user_prompt, similar_examples, analysis
            )
            
            if optimized:
                ai_model = "Gemini Pro (RAG)"
                rag_mode = "Gemini RAG"
            else:
                optimized = self.fallback_optimizer.optimize_prompt(
                    user_prompt, similar_examples, analysis
                )
                ai_model = "Fallback Optimizer"
                rag_mode = "Fallback"
        else:
            optimized = self.fallback_optimizer.optimize_prompt(
                user_prompt, similar_examples, analysis
            )
            ai_model = "Fallback Optimizer (Gemini N/A)"
            rag_mode = "Fallback"
        
        improvement = max(0, (1.0 - analysis['overall_score']) * 100)
        
        # RETURN - rag_mode her zaman var!
        return {
            'original_prompt': user_prompt,
            'analysis': analysis,
            'similar_examples': similar_prompts,
            'optimized_prompt': optimized,
            'improvement_percentage': improvement,
            'generative_ai_used': self.gemini_agent.available,
            'ai_model': ai_model,
            'rag_mode': rag_mode  # ← BU HER ZAMAN VAR!
        }

# ==================== GLOBAL INSTANCE ====================
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

try:
    promptlab = GeminiPromptLabRAG(gemini_api_key=GEMINI_KEY)
    print("✅ PromptLab global instance oluşturuldu")
except Exception as e:
    print(f"❌ PromptLab hatası: {e}")
    promptlab = None

if __name__ == "__main__":
    print("\n🧪 Test başlıyor...")
    if promptlab:
        result = promptlab.process_prompt("test prompt")
        print(f"✅ Test başarılı!")
        print(f"   Keys: {list(result.keys())}")
        print(f"   RAG Mode: {result['rag_mode']}")
    else:
        print("❌ PromptLab yüklenemedi!")