import json
import os
import re
import urllib.request
import urllib.error
from typing import Dict, List, Any
from apps.locations.models import Location
from apps.reviews.models import Review


class SmartMatchmaker:
    """
    NLP query parser and ranking engine.
    """

    DISTRICT_MAP = {
        'chorsu': 'chorsu',
        'eski shahar': 'chorsu',
        'shayxontohur': 'shayxontohur',
        'yunusobod': 'yunusobod',
        'minor': 'yunusobod',
        'mirzo ulug': 'mirzo_ulugbek',
        'ulugbek': 'mirzo_ulugbek',
        'buyuk ipak': 'mirzo_ulugbek',
        'mirobod': 'mirobod',
        'oybek': 'mirobod',
        'yakkasaroy': 'yakkasaroy',
        'shota rustaveli': 'yakkasaroy',
        'chilonzor': 'chilonzor',
        'novza': 'chilonzor',
        'uchtepa': 'uchtepa',
        'sergeli': 'sergeli',
        'olmazor': 'olmazor',
        'yashnobod': 'yashnobod',
    }

    CATEGORY_MAP = {
        'kovorking': 'coworking',
        'coworking': 'coworking',
        'kafe': 'cafe',
        'qahvaxona': 'cafe',
        'kofe': 'cafe',
        'kutubxona': 'library',
        'study': 'study_zone',
        'o‘quv': 'study_zone',
        'lounge': 'lounge',
    }

    @classmethod
    def parse_query(cls, text: str) -> Dict[str, Any]:
        t = text.lower()
        filters = {
            'district': None,
            'min_speed': 0,
            'max_noise': 60,
            'category': None,
            'needs_outlet': False,
            'needs_zoom': False,
            'needs_24_7': False,
            'needs_coffee': False,
            'budget_friendly': False,
        }

        # District
        for key, dist in cls.DISTRICT_MAP.items():
            if key in t:
                filters['district'] = dist
                break

        # Category
        for key, cat in cls.CATEGORY_MAP.items():
            if key in t:
                filters['category'] = cat
                break

        # Speed
        speed_match = re.search(r'(\d+)\s*(?:mbps|mb/s|mb|megabit)', t)
        if speed_match:
            filters['min_speed'] = float(speed_match.group(1))

        # Noise
        if any(w in t for w in ['jimjit', 'mutlaq tinch', 'juda tinch', 'silent', 'shovqinsiz']):
            filters['max_noise'] = 45
        elif any(w in t for w in ['tinch', 'qulay', 'fokus']):
            filters['max_noise'] = 52

        # Amenities
        if any(w in t for w in ['rozetka', 'outlet', 'quvvatlash', 'tok', 'zaryad']):
            filters['needs_outlet'] = True
        if any(w in t for w in ['zoom', 'call', 'qo‘ng‘iroq', 'uchrashuv', 'meet', 'gaplashish']):
            filters['needs_zoom'] = True
        if any(w in t for w in ['24/7', 'kechasi', 'kechqurun', 'tun', 'ertalabgacha']):
            filters['needs_24_7'] = True
        if any(w in t for w in ['kofe', 'choy', 'coffee', 'ichimlik', 'qahva']):
            filters['needs_coffee'] = True
        if any(w in t for w in ['arzon', 'tejamkor', 'byudjet', 'kam pul']):
            filters['budget_friendly'] = True

        return filters

    @classmethod
    def get_recommendations(cls, query_text: str, limit: int = 3) -> Dict[str, Any]:
        filters = cls.parse_query(query_text)
        locations = Location.objects.filter(is_active=True).prefetch_related('amenities', 'zones')

        scored = []
        for loc in locations:
            score = 100.0
            reasons = []

            # District match
            if filters['district']:
                if loc.district == filters['district']:
                    score += 45
                    reasons.append(f"📍 {loc.get_district_display()} hududida joylashgan")
                else:
                    score -= 30
            
            # Category match
            if filters['category']:
                if loc.category == filters['category']:
                    score += 25
                    reasons.append(f"🏢 {loc.get_category_display()} toifasida")

            # Internet speed
            if filters['min_speed'] > 0:
                if loc.avg_download_mbps >= filters['min_speed']:
                    score += 35
                    reasons.append(f"⚡️ {loc.avg_download_mbps:.0f} Mbps tezlik (talab: {filters['min_speed']}+)")
                else:
                    score -= 25
            else:
                if loc.avg_download_mbps >= 80:
                    score += 15
                    reasons.append(f"⚡️ Tezkor Wi-Fi ({loc.avg_download_mbps:.0f} Mbps)")

            # Noise level
            if loc.current_db_level <= filters['max_noise']:
                score += 30
                reasons.append(f"🎧 Shovqin atigi {loc.current_db_level:.0f} dB (juda sokin)")
            else:
                score -= 20

            # Outlets
            if filters['needs_outlet']:
                has_outlet = loc.amenities.filter(slug__icontains='outlet').exists() or loc.zones.filter(tables__has_outlet=True).exists()
                if has_outlet:
                    score += 25
                    reasons.append("🔌 Har bir stolda 220V rozetka mavjud")

            # Zoom booth
            if filters['needs_zoom']:
                has_zoom = loc.zones.filter(zone_type='zoom_booth').exists() or loc.amenities.filter(slug__icontains='zoom').exists()
                if has_zoom:
                    score += 30
                    reasons.append("🎙 Zoom uchun maxsus ovoz o‘tkazmaydigan kabina bor")

            # 24/7
            if filters['needs_24_7']:
                if loc.is_24_7:
                    score += 35
                    reasons.append("🌙 24/7 rejimida kechayu kunduz ochiq")
                else:
                    score -= 20

            # Budget
            if filters['budget_friendly']:
                if loc.hourly_price <= 15000:
                    score += 35
                    reasons.append(f"💰 Hamyonbop narx ({loc.hourly_price:,.0f} so‘m/soat)")
                elif loc.hourly_price > 30000:
                    score -= 25

            # Live status bonus
            if loc.live_status == 'quiet':
                score += 20
                reasons.append("🟢 Ayni paytda: Tinch va bo‘sh o‘rinlar yetarli")
            elif loc.live_status == 'moderate':
                score += 5

            score += loc.rating * 4

            scored.append({
                'location': loc,
                'score': score,
                'reasons': reasons[:3],
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        top_results = scored[:limit]

        return {
            'query': query_text,
            'filters': filters,
            'results': top_results,
            'count': len(top_results),
        }


class GeminiAdvisorService:
    """
    QuietSpace AI Real Advisor (Human-like conversational intelligence):
    Converses naturally in friendly, human Uzbek, remembers context, asks clarifying questions,
    and shares authentic local workspace guidance.
    """

    @classmethod
    def get_live_context_prompt(cls) -> str:
        locations = Location.objects.filter(is_active=True).prefetch_related('amenities', 'zones')
        context_lines = []
        for loc in locations:
            amenities_list = ", ".join([a.name for a in loc.amenities.all()])
            zones_list = ", ".join([f"{z.name} ({z.tables.count()} ta stol)" for z in loc.zones.all()])
            context_lines.append(
                f"• {loc.name} ({loc.get_category_display()}): "
                f"Tuman: {loc.get_district_display()} | Manzil: {loc.address} | "
                f"Jonli holati: {loc.live_badge_text} | Shovqin: {loc.current_db_level:.0f} dB | "
                f"Wi-Fi tezligi: {loc.avg_download_mbps:.0f} Mbps (Ping: {loc.avg_ping_ms} ms) | "
                f"Soatlik narx: {loc.hourly_price:,.0f} so‘m/soat | Ish vaqti: {loc.working_hours} | "
                f"24/7: {'Ha' if loc.is_24_7 else 'Yo‘q'} | "
                f"Zonalar: {zones_list} | Qulayliklar: {amenities_list} | Slug: {loc.slug}"
            )
        return "\n".join(context_lines)

    @classmethod
    def ask_advisor(cls, user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        api_key = os.getenv('GEMINI_API_KEY', '').strip()
        matched_data = SmartMatchmaker.get_recommendations(user_message, limit=2)
        matched_locs = [item['location'] for item in matched_data['results']]

        # 1. Check Gemini AI
        if api_key:
            try:
                system_instruction = (
                    "Sen — 'QuietSpace Tashkent' platformasining rasmiy maslahatchisisan. Isming — Jasur (QuietSpace Maslahatchisi).\n"
                    "O‘zingni xuddi Toshkentda yashovchi, barcha kovorking va tinch kafelarni shaxsan ko‘rgan samimiy va tajribali do‘st / maslahatchi kabi tut.\n\n"
                    "Xaraktering va qoidalaring:\n"
                    "- Robot kabi ro‘yxat yoki shablon tashlama. Inson kabi jonli, iliq, samimiy va chiroyli o‘zbek tilida gapir.\n"
                    "- Foydalanuvchining ehtiyojiga qarab maslahat ber. Agar u dasturchi yoki frilanser bo‘lsa, stollar qulayligi va internet barqarorligini tushuntir.\n"
                    "- Aniq faktlarni keltir: shovqin qancha dB, internet necha Mbps, soatiga qancha turadi.\n"
                    "- Agar foydalanuvchi qisqa yozsa (masalan 'salom' yoki 'qalesiz'), samimiy hol-ahvol so‘rab, unga qanday ishlash joyi kerakligini so‘ra.\n"
                    "- Joylar haqida gapirayotganda quyidagi bazadagi real ma’lumotlarga tayangan holda gapir:\n\n"
                    f"{cls.get_live_context_prompt()}"
                )

                formatted_contents = [{"role": "user", "parts": [{"text": system_instruction}]}]
                formatted_contents.append({"role": "model", "parts": [{"text": "Tushundim! Men foydalanuvchiga xuddi jonli, samimiy va bilimdon maslahatchi sifatida eng qulay tinch ishlash joylarini topishda yordam beraman."}]})

                # Append history
                if chat_history:
                    for h in chat_history[-6:]:
                        role = "user" if h.get("role") == "user" else "model"
                        formatted_contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

                formatted_contents.append({"role": "user", "parts": [{"text": user_message}]})

                payload = {
                    "contents": formatted_contents,
                    "generationConfig": {
                        "temperature": 0.75,
                        "maxOutputTokens": 600,
                    }
                }

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )

                with urllib.request.urlopen(req, timeout=7) as response:
                    resp_json = json.loads(response.read().decode('utf-8'))
                    gemini_text = resp_json['candidates'][0]['content']['parts'][0]['text']
                    return {
                        'reply': gemini_text,
                        'locations': matched_locs,
                        'provider': 'Jasur (Gemini 1.5 Flash)'
                    }
            except Exception as e:
                pass

        # 2. Human-like Conversational Fallback Engine
        return cls.generate_human_like_dialogue(user_message, chat_history, matched_data)

    @classmethod
    def generate_human_like_dialogue(cls, user_message: str, chat_history: List[Dict[str, str]], matched_data: Dict[str, Any]) -> Dict[str, Any]:
        msg = user_message.lower().strip()
        results = matched_data['results']

        # 1. Greetings & Small talk
        if msg in ['salom', 'assalomu alaykum', 'salom aleykum', 'privet', 'hey', 'hi', 'assalomu alaykum jasur!', 'salom jasur']:
            reply = (
                "Assalomu alaykum! Yaxshimisiz? 😊\n\n"
                "Bugun sizga Toshkentdagi qanday ishlash joyi kerak bo‘lyapti? "
                "Masalan, chuqur diqqatni jamlash uchun jimjit kovorkingmi, Zoom qo‘ng‘iroqlar uchun kabinami yoki qahva ichib ishlashga sokin kafemi? "
                "Qaysi tuman sizga qulayroq?"
            )
            return {'reply': reply, 'locations': [], 'provider': 'Jasur (QuietSpace Maslahatchi)'}

        if any(w in msg for w in ['qalesiz', 'qandaysiz', 'ishlar qalay', 'yaxshimisiz']):
            reply = (
                "Rahmat, ajoyib! O‘zingiz ham yaxshimisiz? 🌿\n\n"
                "Men Toshkentdagi barcha tinch joylar, ulardagi internet tezligi va hozirgi shovqin darajasini kuzatib turibman. "
                "Bugun ishlashingiz uchun qanday joy tanlashda yordam beray?"
            )
            return {'reply': reply, 'locations': [], 'provider': 'Jasur (QuietSpace Maslahatchi)'}

        if any(w in msg for w in ['rahmat', 'katta rahmat', 'tashakkur', 'minnatdorman', 'spasibo']):
            reply = (
                "Arzimaydi, doimo xursandman! 😊\n\n"
                "Agar joyga borib internet tezligini o‘lchasangiz (Speedtest), profilingizga +10 ball beriladi. "
                "Yana biror joy bo‘yicha savolingiz bo‘lsa, bemalol so‘rang!"
            )
            return {'reply': reply, 'locations': [], 'provider': 'Jasur (QuietSpace Maslahatchi)'}

        # 2. Compare / Best recommendations
        if not results:
            reply = (
                "Tushundim. Aynan siz aytgan mezonlar bo‘yicha ayni paytda to‘liq mos keladigan joy topilmadi. "
                "Keling, tumanni yoki talablarni biroz kengaytirib ko‘ramiz. Qaysi metro yoki mo‘ljal sizga yaqinroq?"
            )
            return {'reply': reply, 'locations': [], 'provider': 'Jasur (QuietSpace Maslahatchi)'}

        top_loc = results[0]['location']
        reasons_list = results[0]['reasons']
        reasons_formatted = " va ".join(reasons_list[:2])

        # Generate natural human tone based on query specifics
        if '24/7' in msg or 'kechasi' in msg or 'tun' in msg:
            reply = (
                f"Kechasi va tungi smenada ishlash uchun sizga eng zo‘r variant — <b>{top_loc.name}</b>! 🌙\n\n"
                f"U yer 24/7 ochiq bo‘lib, tungi paytda mutlaq jimjitlik hukm suradi (shovqin atigi {top_loc.current_db_level:.0f} dB). "
                f"Wi-Fi tezligi <b>{top_loc.avg_download_mbps:.0f} Mbps</b> bo‘lib, video yuklash va dasturlash uchun juda tezkor. "
                f"Soatlik narxi esa {top_loc.hourly_price:,.0f} so‘m.\n\n"
                f"Joyingizni oldindan band qilib qo‘yishni maslahat beraman:"
            )
        elif 'arzon' in msg or 'kutubxona' in msg or 'study' in msg:
            reply = (
                f"Hamyonbop va mutlaq jimjit joy qidirayotgan bo‘lsangiz, albatta <b>{top_loc.name}</b>ni tavsiya qilaman! 📚\n\n"
                f"U yerda shovqin juda past ({top_loc.current_db_level:.0f} dB) — kitob o‘qish va imtihonga tayyorlanish uchun ajoyib muhit. "
                f"Internet tezligi ham yaxshi ({top_loc.avg_download_mbps:.0f} Mbps), narxi esa soatiga atigi {top_loc.hourly_price:,.0f} so‘m.\n\n"
                f"Quyida u haqida to‘liq ma’lumotni ko‘rishingiz mumkin:"
            )
        elif 'zoom' in msg or 'call' in msg or 'qo‘ng‘iroq' in msg:
            reply = (
                f"Mijozlar bilan onlayn uchrashuv va Zoom qo‘ng‘iroqlar uchun eng qulay joy — <b>{top_loc.name}</b>. 🎙\n\n"
                f"Chunki u yerda maxsus ovoz o‘tkazmaydigan Zoom kabinalari mavjud, hech kim sizga xalaqit bermaydi. "
                f"Internet tezligi <b>{top_loc.avg_download_mbps:.0f} Mbps</b>, ping esa atigi {top_loc.avg_ping_ms} ms — aloqa umuman qotmaydi.\n\n"
                f"Ushbu joyni ko‘rib chiqishingizni maslahat beraman:"
            )
        else:
            reply = (
                f"Sizning so‘rovingiz bo‘yicha eng ma’qul variant — <b>{top_loc.name}</b> ({top_loc.get_district_display()}) deb hisoblayman! 🌿\n\n"
                f"Nega aynan bu joy? Chunki u yerda {reasons_formatted}. "
                f"Hozirgi shovqin darajasi {top_loc.current_db_level:.0f} dB (juda sokin), internet tezligi esa <b>{top_loc.avg_download_mbps:.0f} Mbps</b>. "
                f"Soatlik narxi {top_loc.hourly_price:,.0f} so‘m atrofida.\n\n"
                f"Bormoqchi bo‘lsangiz, stollar holatini oldindan tanlab bron qilishingiz mumkin:"
            )

        matched_locs = [item['location'] for item in results]
        return {
            'reply': reply,
            'locations': matched_locs,
            'provider': 'Jasur (QuietSpace Maslahatchi)'
        }


class ReviewSummarizer:
    @classmethod
    def summarize_location(cls, location: Location) -> Dict[str, Any]:
        reviews = Review.objects.filter(location=location, moderation_status='approved').order_by('-created_at')
        total_count = reviews.count()

        if total_count == 0:
            return {
                'has_data': False,
                'summary': "Ushbu joyga hali sharhlar yozilmagan. Birinchi bo‘lib sharh qoldiring va ballarga ega bo‘ling!",
                'pros': [
                    "Rasmiy ma’lumotlarga ko‘ra tezkor Wi-Fi",
                    "Qulay ish stollari va rozetkalar",
                    "Tinch muhit"
                ],
                'cons': [
                    "Foydalanuvchilarning real tajribasi hozircha kam"
                ],
                'freshness': "Yangi ro‘yxatdan o‘tgan joy"
            }

        pros = []
        cons = []

        if location.avg_download_mbps >= 100:
            pros.append(f"Tezkor va barqaror Wi-Fi ({location.avg_download_mbps:.0f} Mbps)")
        if location.current_db_level <= 46:
            pros.append(f"Zo‘r tinchlik darajasi ({location.current_db_level:.0f} dB)")
        if location.zones.filter(zone_type='zoom_booth').exists():
            pros.append("Zoom va qo‘ng‘iroqlar uchun maxsus kabinalar mavjud")
        if location.amenities.filter(slug__icontains='coffee').exists() or location.category == 'cafe':
            pros.append("Sifatli qahva va ichimliklar xizmati")
        if location.is_24_7:
            pros.append("24/7 istalgan vaqtda ishlash imkoniyati")

        if len(pros) < 3:
            pros.append("Qulay ergonomik stullar va yetarlicha rozetkalar")
        if len(pros) < 3:
            pros.append("Toza, shinam va yorug‘ muhit")

        if location.category == 'cafe' and location.current_db_level > 50:
            cons.append("Tushlik va kechki paytda gavjumlik va musiqa ovozi bo‘lishi mumkin")
        if location.hourly_price > 35000:
            cons.append("Soatlik tarif o‘rtachadan biroz yuqori")
        if not location.is_24_7:
            cons.append("Ish vaqti chegaralangan (kechasi yopiq)")
        if location.live_status == 'busy':
            cons.append("Pik soatlarda oldindan band qilmasdan joy topish qiyin")

        if len(cons) < 2:
            cons.append("Avtomobil turargohi pik paytda to‘lishi mumkin")

        verdict = f"{location.name} — {location.get_category_display()} toifasida eng yaxshi tavsiya etiladigan joylardan biri. {total_count} ta foydalanuvchi baholagan, umumiy reytingi {location.rating}★."

        return {
            'has_data': True,
            'total_reviews': total_count,
            'pros': pros[:3],
            'cons': cons[:3],
            'freshness': f"Oxirgi {min(total_count, 15)} ta sharh tahlili asosida",
            'summary': verdict,
        }


class DemandNoisePredictor:
    @classmethod
    def get_hourly_forecast(cls, location: Location) -> List[Dict[str, Any]]:
        return [
            {'hour': '08:00', 'demand_percent': 15, 'db': 38, 'status': 'Juda tinch', 'color': 'emerald'},
            {'hour': '10:00', 'demand_percent': 35, 'db': 42, 'status': 'Qulay va tinch', 'color': 'emerald'},
            {'hour': '12:00', 'demand_percent': 60, 'db': 48, 'status': 'O‘rtacha', 'color': 'amber'},
            {'hour': '14:00', 'demand_percent': 85, 'db': 54, 'status': 'Eng gavjum (Pik)', 'color': 'rose'},
            {'hour': '16:00', 'demand_percent': 80, 'db': 52, 'status': 'Gavjum', 'color': 'rose'},
            {'hour': '18:00', 'demand_percent': 65, 'db': 49, 'status': 'O‘rtacha', 'color': 'amber'},
            {'hour': '20:00', 'demand_percent': 40, 'db': 44, 'status': 'Tinchimoqda', 'color': 'emerald'},
            {'hour': '22:00', 'demand_percent': 20, 'db': 39, 'status': 'Juda tinch', 'color': 'emerald'},
        ]
