from django.urls import path
from . import views
from .views import EventListView, EventDetailView

urlpatterns = [
# 1. メイン画面
    path('', views.index, name='index'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),

    # 2. モード切り替え（セッション管理）
    # JSから location.href = `/events/{{ event.slug }}/enter/${programNum}/director/` で呼ばれる場所
    path('events/<slug:slug>/enter/<str:program_num>/<str:mode>/', views.enter_mode, name='enter_mode'),
    
    # ログアウト処理（指示削除 ＋ セッション破棄）
    path('events/<slug:slug>/exit/', views.exit_mode, name='exit_mode'),

    # 3. 各モードの表示
    # アナウンサーモード
    path('events/<slug:event_slug>/A/<str:program_num>/', views.announcer_mode_view, name='announcer_mode'),
    
    # ディレクターモード
    path('events/<slug:event_slug>/D/<str:program_num>/', views.director_mode_view, name='director_mode'),
]