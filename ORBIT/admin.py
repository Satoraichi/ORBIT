from django.contrib import admin
from .models import *

class ProgramInline(admin.TabularInline): # 表形式で入力できる設定
    model = Program
    fields = ('order', 'number', 'name', 'member_c', 'member_d', 'member_ann', 'manuscript_pdf')
    extra = 1

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('year',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiscal_year', 'slug')
    prepopulated_fields = {'slug': ('name',)} # 名前からslugを自動生成
    inlines = [ProgramInline]

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('grade', 'family_name', 'first_name', 'family_kana', 'first_kana')
    list_filter = ('grade',) # 学年で絞り込み
    search_fields = ('family_name', 'first_name', 'family_kana', 'first_kana') # 名前やふりがなで検索可能

@admin.register(ProgramChange)
class ProgramChangeAdmin(admin.ModelAdmin):
    list_display = ('program', 'before_text', 'after_text', 'created_at')
    list_filter = ('program__event',)
    search_fields = ('before_text', 'after_text', 'program__name')

@admin.register(DirectorInstruction)
class DirectorInstructionAdmin(admin.ModelAdmin):
    list_display = ('event', 'action_type', 'created_at')
    list_filter = ('event', 'action_type')
    # 指示は新しい順に並んでいた方が管理しやすい
    ordering = ('-created_at',)