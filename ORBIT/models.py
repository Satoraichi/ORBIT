from django.db import models
from django.urls import reverse

class Participant(models.Model):
    # 学年の選択肢を定義
    GRADE_CHOICES = [
        (1, '中学1年'), (2, '中学2年'), (3, '中学3年'),
        (4, '高校1年'), (5, '高校2年'), (6, '高校3年'),
        (0, 'その他'),
    ]

    grade = models.PositiveSmallIntegerField("学年", choices=GRADE_CHOICES, default=1)
    family_name = models.CharField("姓", max_length=100)
    first_name = models.CharField("名", max_length=100)
    family_kana = models.CharField("せい", max_length=100, blank=True ,null=True)
    first_kana = models.CharField("めい", max_length=100, blank=True ,null=True)

    class Meta:
        verbose_name = "登録メンバー"
        verbose_name_plural = "登録メンバー"
        ordering = ['grade', 'family_kana', 'first_kana']

    def __str__(self):
        return f"{self.get_grade_display()} - {self.family_name}"

class FiscalYear(models.Model):
    year = models.PositiveIntegerField("年度", unique=True)
    is_current = models.BooleanField("現在の年度", default=False)

    def __str__(self):
        return f"{self.year}年度"

class Event(models.Model):
    fiscal_year = models.ForeignKey(
        FiscalYear, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name="年度",
        null=True, 
        blank=True
    )
    name = models.CharField("イベント名", max_length=200)
    date = models.DateField("開催日", null=True, blank=True)
    is_permanent = models.BooleanField("常設（通年）", default=False)
    slug = models.SlugField("URL名", max_length=100, unique=True)

    class Meta:
        verbose_name = "イベント・常設枠"

    def __str__(self):
        prefix = "[常設] " if self.is_permanent else ""
        return f"{prefix}{self.name} ({self.fiscal_year})"

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
def program_pdf_path(instance, filename):
    # 保存先を 'manuscripts/イベント名/プログラム番号.pdf' に整理する
    return f'manuscripts/{instance.event.slug}/{instance.number}_{filename}'
    
class Program(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name="大会"
    )
    order = models.PositiveIntegerField("表示順", default=0, help_text="数字が小さい順に並びます")
    number = models.CharField("プログラム番号", max_length=10, help_text="例: A-1, 101 など", null=True, blank=True,)
    name = models.CharField("プログラム名", max_length=200, null=True, blank=True,)

    member_c = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs_c',
        verbose_name="C"
    )
    member_d = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs_d',
        verbose_name="D"
    )
    member_ann = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs_ann',
        verbose_name="ANN"
    )

    manuscript_pdf = models.FileField(
        "原稿PDF", 
        upload_to=program_pdf_path,
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "プログラム"
        verbose_name_plural = "プログラム"
        ordering = ['order']  # デフォルトのソート順を「表示順」に設定

    def __str__(self):
        return f"{self.number}: {self.name}"
    
class ProgramChange(models.Model):
    """プログラム変更事項（Before/After）"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='changes')
    before_text = models.TextField("変更前")
    after_text = models.TextField("変更後")
    created_at = models.DateTimeField(auto_now_add=True)

class DirectorInstruction(models.Model):
    """ディレクターからのクイック指示（アイコンベース）"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # 30, 15, 5, circle, skip_next, close, stop_circle など
    action_type = models.CharField("アイコン名", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)