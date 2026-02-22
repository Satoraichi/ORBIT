from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import *

def index(request):
    # templates/ORBIT/index.html を探しにいく設定
    return render(request, 'ORBIT/index.html')

class EventListView(ListView):
    model = Event
    template_name = 'ORBIT/events_list.html'
    context_object_name = 'events'
    ordering = ['-is_permanent', '-fiscal_year__year', 'date']

class EventDetailView(DetailView):
    model = Event
    template_name = 'ORBIT/events_detail.html'

# モード開始（ログイン的な役割）
def enter_mode(request, slug, program_num, mode): # 引数をURL設計に合わせる
    # セッションに「実行中のイベント」「プログラム番号」「モード」を記録
    request.session['active_event_slug'] = slug
    request.session['active_program_num'] = program_num
    request.session['active_mode'] = mode
    
    # セッションを即時保存（念のため）
    request.session.modified = True
    
    if mode == 'director':
        return redirect('director_mode', event_slug=slug, program_num=program_num)
    return redirect('announcer_mode', event_slug=slug, program_num=program_num)

def exit_mode(request, slug):
    # 1. 指示を削除
    event = get_object_or_404(Event, slug=slug)
    DirectorInstruction.objects.filter(event=event).delete()
    
    # 2. セッションから特定のキーだけを削除する
    # flush() は使わず、pop で個別に消すことでログイン状態を維持します
    keys_to_clear = ['active_event_slug', 'active_program_num', 'active_mode']
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]
            
    # 明示的にセッションの変更を保存
    request.session.modified = True
        
    return redirect('event_detail', slug=slug)

def announcer_mode_view(request, event_slug, program_num):
    event = get_object_or_404(Event, slug=event_slug)
    program = get_object_or_404(Program, event=event, number=program_num)
    
    # 最新の指示を10件取得して、作成日順に並べる
    instructions = DirectorInstruction.objects.filter(event=event).order_by('-created_at')[:10]
    
    # プログラム変更情報も一緒に渡す（後の「変更」タブ用）
    changes = ProgramChange.objects.filter(program=program)

    context = {
        'event': event,
        'program': program,
        'instructions': instructions,
        'changes': changes,
    }
    return render(request, 'ORBIT/announcer_mode.html', context)

def director_mode_view(request, event_slug, program_num):
    event = get_object_or_404(Event, slug=event_slug)
    # ディレクターも現在どのプログラムを見ているか把握するために取得
    program = get_object_or_404(Program, event=event, number=program_num)
    
    instructions = DirectorInstruction.objects.filter(event=event).order_by('-created_at')[:15]
    
    return render(request, 'ORBIT/director_mode.html', {
        'event': event,
        'program': program,
        'instructions': instructions,
    })

def clear_instructions_and_logout(request, slug):
    # 特定のイベントの指示をすべて削除
    event = Event.objects.get(slug=slug)
    Instruction.objects.filter(event=event).delete()
    
    # 削除後、本来のログアウト先やイベント詳細へリダイレクト
    return redirect('event_detail', slug=slug)