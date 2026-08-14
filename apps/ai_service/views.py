import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from apps.locations.models import Location
from .models import AISearchLog
from .services import SmartMatchmaker, GeminiAdvisorService, ReviewSummarizer, DemandNoisePredictor


@csrf_exempt
def ai_chat_api(request):
    """
    QuietSpace AI Real Advisor Chat API:
    Integrates Google Gemini / Intelligent Advisor Engine with interactive workspace cards.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST metodi talab qilinadi'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        chat_history = data.get('history', [])

        if not user_message:
            return JsonResponse({'status': 'error', 'message': 'Xabar matni bo‘sh bo‘lishi mumkin emas'}, status=400)

        # Call Gemini AI / Advisor Service
        advisor_res = GeminiAdvisorService.ask_advisor(user_message, chat_history)
        reply_text = advisor_res['reply']
        matched_locs = advisor_res['locations']
        provider = advisor_res.get('provider', 'QuietSpace AI')

        serialized_locations = []
        loc_ids = []
        for loc in matched_locs:
            loc_ids.append(loc.id)
            serialized_locations.append({
                'id': loc.id,
                'name': loc.name,
                'slug': loc.slug,
                'district': loc.get_district_display(),
                'category': loc.get_category_display(),
                'address': loc.address,
                'cover_image': loc.cover_image.url if loc.cover_image else '',
                'live_status': loc.live_status,
                'live_status_text': loc.live_badge_text,
                'current_db_level': loc.current_db_level,
                'avg_download_mbps': loc.avg_download_mbps,
                'hourly_price': float(loc.hourly_price),
                'rating': float(loc.rating),
                'url': f"/locations/{loc.slug}/",
            })

        # Save AI Log
        user = request.user if request.user.is_authenticated else None
        AISearchLog.objects.create(
            user=user,
            query_text=user_message,
            recommended_location_ids=loc_ids,
            explanation=f"Provider: {provider} | {len(serialized_locations)} ta joy"
        )

        return JsonResponse({
            'status': 'success',
            'reply': reply_text,
            'locations': serialized_locations,
            'provider': provider
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def smart_matchmaker_api(request):
    """Legacy API fallback for direct search query ranking"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST metodi talab qilinadi'}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        if not query:
            return JsonResponse({'status': 'error', 'message': 'Qidiruv so‘rovi bo‘sh bo‘lishi mumkin emas'}, status=400)

        match_data = SmartMatchmaker.get_recommendations(query, limit=3)
        results = []
        loc_ids = []

        for item in match_data['results']:
            loc: Location = item['location']
            loc_ids.append(loc.id)
            results.append({
                'id': loc.id,
                'name': loc.name,
                'slug': loc.slug,
                'district': loc.get_district_display(),
                'category': loc.get_category_display(),
                'address': loc.address,
                'cover_image': loc.cover_image.url if loc.cover_image else '',
                'live_status': loc.live_status,
                'live_status_text': loc.live_badge_text,
                'current_db_level': loc.current_db_level,
                'avg_download_mbps': loc.avg_download_mbps,
                'hourly_price': float(loc.hourly_price),
                'rating': float(loc.rating),
                'reasons': item['reasons'],
                'score': item['score'],
                'url': f"/locations/{loc.slug}/",
            })

        return JsonResponse({
            'status': 'success',
            'query': query,
            'results': results,
            'total': len(results),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def ai_assistant_view(request):
    initial_query = request.GET.get('q', '').strip()
    return render(request, 'ai_service/ai_assistant.html', {'initial_query': initial_query})
