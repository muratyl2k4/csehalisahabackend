import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Team
from PIL import Image


def secure_file_upload(instance, filename):
    """Secure file upload (uuid + extension)"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('player_photos/', filename)


class Player(models.Model):
    """Player Profile (User related)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    
    current_team = models.ForeignKey(
        Team, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='players',
        verbose_name='Güncel Takım'
    )

    # Verification Fields
    is_email_verified = models.BooleanField(default=False, verbose_name='E-posta Doğrulandı mı?')
    verification_code = models.CharField(max_length=6, blank=True, null=True, verbose_name='Doğrulama Kodu')
    verification_code_created_at = models.DateTimeField(blank=True, null=True, verbose_name='Kod Oluşturulma Tarihi')
    

    #It comes from user's First Name and Last Name
    name = models.CharField(max_length=100, verbose_name='Görünen Ad') # Sahadaki ismi

    age = models.IntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(60)],
        verbose_name='Yaş',
        default=20
    )
    
    photo = models.ImageField(
        upload_to=secure_file_upload, 
        verbose_name='Fotoğraf',
        blank=True,
        null=True
    )

    POSITION_CHOICES = [
        ('KL', 'Kaleci'),
        ('SLB', 'Sol Bek'),
        ('SGB', 'Sağ Bek'),
        ('STP', 'Stoper'),
        ('DOS', 'Defansif Orta Saha'),
        ('MO', 'Merkez Orta Saha'),
        ('MOO', 'Merkez Ofansif Orta Saha'),
        ('SLK', 'Sol Kanat'),
        ('SGK', 'Sağ Kanat'),
        ('ST', 'Santrafor'),
    ]

    position = models.CharField(
        max_length=3,
        choices=POSITION_CHOICES,
        verbose_name='Pozisyon',
        default='ST'
    )
    
    jersey_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name='Forma Numarası',
        null=True,
        blank=True
    )

    FOOT_CHOICES = [
        ('right', 'Sağ'),
        ('left', 'Sol'),
        ('both', 'Her İkisi')
    ]

    preferred_foot = models.CharField(
        max_length=10,
        choices=FOOT_CHOICES,
        verbose_name='Ayak Tercihi',
        default='right'
    )

    # --- Outfield Stats ---
    pace = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Hız (PAC)')
    shooting = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Şut (SHO)')
    passing = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Pas (PAS)')
    dribbling = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Dribling (DRI)')
    defense = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Defans (DEF)')
    physical = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Fizik (PHY)')

    # --- Goalkeeper Stats ---
    diving = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Uçma (DIV)')
    handling = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Elle Kontrol (HAN)')
    kicking = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Degaj (KIC)')
    reflexes = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Refleks (REF)')
    speed = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Hız (SPD)')
    positioning = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(99)], verbose_name='Yer Tutma (POS)')

    overall = models.IntegerField(default=50, verbose_name='Overall', editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Oyuncu'
        verbose_name_plural = 'Oyuncular'
        ordering = ['-overall', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.position})"



    ##Gemini's base calculations 
    ##TODO: Make it more accurate and write clean
    def calculate_overall(self):
        """Calculate overall based on position"""
        p = self.position
        
        if p == 'KL':
            # REF(22%), DIV(22%), POS(20%), HAN(18%), KIC(10%), SPD(8%)
            score = (
                self.reflexes * 0.22 +
                self.diving * 0.22 +
                self.positioning * 0.20 +
                self.handling * 0.18 +
                self.kicking * 0.10 +
                self.speed * 0.08
            )
        elif p == 'ST':
            # ST (Santrafor),15,45,5,20,0,15 (PAC, SHO, PAS, DRI, DEF, PHY)
            score = (
                self.shooting * 0.45 +
                self.dribbling * 0.20 +
                self.pace * 0.15 +
                self.physical * 0.15 +
                self.passing * 0.05
            )
        elif p in ['SLK', 'SGK']:
            # Kanat: PAC(35%), DRI(25%), PAS(20%), SHO(15%), PHY(5%)
            score = (
                self.pace * 0.35 +
                self.dribbling * 0.25 +
                self.passing * 0.20 +
                self.shooting * 0.15 +
                self.physical * 0.05
            )
        elif p == 'MOO':
            # MOO: PAS(35%), DRI(30%), SHO(20%), PAC(10%), PHY(5%)
            score = (
                self.passing * 0.35 +
                self.dribbling * 0.30 +
                self.shooting * 0.20 +
                self.pace * 0.10 +
                self.physical * 0.05
            )
        elif p == 'MO':
            # MO: PAS(30%), DRI(20%), PHY(15%), PAC(10%), SHO(15%), DEF(10%)
            score = (
                self.passing * 0.30 +
                self.dribbling * 0.20 +
                self.physical * 0.15 +
                self.shooting * 0.15 +
                self.pace * 0.10 +
                self.defense * 0.10
            )
        elif p == 'DOS':
            # DOS: DEF(30%), PHY(25%), PAS(20%), PAC(10%), DRI(10%), SHO(5%)
            score = (
                self.defense * 0.30 +
                self.physical * 0.25 +
                self.passing * 0.20 +
                self.pace * 0.10 +
                self.dribbling * 0.10 +
                self.shooting * 0.05
            )
        elif p in ['SLB', 'SGB']:
            # Bek: PAC(30), DEF(10), PAS(15), DRI(15), PHY(30) -> Wait user wrote:
            # "Bek,30,0,15,15,30,10" -> Order was PAC, SHO, PAS, DRI, DEF, PHY
            # So: PAC=30, SHO=0, PAS=15, DRI=15, DEF=30, PHY=10
            score = (
                self.pace * 0.30 +
                self.defense * 0.30 +
                self.passing * 0.15 +
                self.dribbling * 0.15 +
                self.physical * 0.10
            )
        elif p == 'STP':
            # STP: DEF(45%), PHY(30%), PAC(15%), PAS(5%), DRI(5%)
            score = (
                self.defense * 0.45 +
                self.physical * 0.30 +
                self.pace * 0.15 +
                self.passing * 0.05 +
                self.dribbling * 0.05
            )
        else:
            score = 50 # Default

        return int(round(score))

    def initialize_stats(self):
        """Initialize stats based on position (~75 Overall) -Gemini"""
        p = self.position
        if p == 'KL':
            self.reflexes, self.diving = 80, 80
            self.positioning, self.handling = 78, 76
            self.kicking, self.speed = 70, 45
        elif p == 'ST':
            self.shooting, self.pace = 78, 78
            self.dribbling, self.physical = 74, 74
            self.passing, self.defense = 60, 35
        elif p in ['SLK', 'SGK']:
            self.pace, self.dribbling = 82, 78
            self.passing, self.shooting = 74, 70
            self.physical, self.defense = 60, 40
        elif p in ['MO', 'MOO']: 
            self.passing, self.dribbling = 80, 77
            self.physical, self.shooting = 72, 72
            self.pace, self.defense = 72, 68
            if p == 'MOO': 
                self.defense = 50
                self.passing = 82
                self.dribbling = 80
                self.passing = 82
                self.dribbling = 80
        elif p == 'DOS':
            self.defense, self.physical = 78, 80
            self.passing, self.pace = 74, 65
            self.dribbling, self.shooting = 68, 55
        elif p in ['SLB', 'SGB']:
            self.pace, self.defense = 78, 76
            self.physical, self.dribbling = 74, 72
            self.passing, self.shooting = 70, 50
        elif p == 'STP':
            self.defense, self.physical = 80, 78
            self.pace, self.passing = 65, 60
            self.dribbling, self.shooting = 55, 40

    def save(self, *args, **kwargs):
        # Sync name from User if linked
        if self.user:
            full_name = self.user.get_full_name()
            if full_name:
                self.name = full_name
        
        # Yeni oyuncu için statları başlat (eğer default ise)
        if not self.pk and self.pace == 50 and self.shooting == 50:
            self.initialize_stats()
        
        self.overall = self.calculate_overall()
        

        ##We don't use image processing anymore (because we are using free pythonanywhere server :(( 
        # if self.photo:
        #     try:
        #         if hasattr(self.photo, 'file') and isinstance(self.photo.file, UploadedFile):
        #             processed = process_image_content(self.photo.file)
        #             if processed:
        #                 self.photo.save(self.photo.name, processed, save=False)
        #     except Exception as e:
        #         print(f"Image processing error: {e}")

        super().save(*args, **kwargs)

    
    @property
    def total_goals(self):
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self).aggregate(total=models.Sum('goals'))['total'] or 0
    
    @property
    def total_assists(self):
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self).aggregate(total=models.Sum('assists'))['total'] or 0
    
    @property
    def matches_played(self):
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self, played=True).count()
