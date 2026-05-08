"""Seed the Spartan Gym database with realistic demo data."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from core.models import (
    Attendance, ClassBooking, ContactMessage, GymClass, Membership,
    Payment, Plan, ProgressLog, SiteSettings, Testimonial, Trainer,
)


class Command(BaseCommand):
    help = "Seed the Spartan Gym DB with demo content."

    def handle(self, *args, **options):
        SiteSettings.load()  # ensure singleton

        # ---- Users ----
        if not User.objects.filter(username="superadmin").exists():
            User.objects.create_user(
                username="superadmin", password="spartan123",
                email="super@spartangym.com", first_name="Leonidas", last_name="King",
                role=User.Role.SUPER_ADMIN,
            )
            self.stdout.write("Created superadmin / spartan123")

        if not User.objects.filter(username="admin").exists():
            u = User.objects.create_user(
                username="admin", password="spartan123",
                email="admin@spartangym.com", first_name="Helena", last_name="Cross",
                role=User.Role.ADMIN,
            )
            u.can_add_member = True
            u.can_edit_member = True
            u.can_manage_classes = True
            u.save()
            self.stdout.write("Created admin / spartan123 (limited perms)")

        if not User.objects.filter(username="member").exists():
            User.objects.create_user(
                username="member", password="spartan123",
                email="member@spartangym.com", first_name="Marcus", last_name="Steel",
                role=User.Role.MEMBER, phone="+1 555 010 4444",
            )
            self.stdout.write("Created member / spartan123")

        # ---- Demo members ----
        member_seed = [
            ("alex.iron", "Alex", "Iron", "alex@example.com"),
            ("sara.thunder", "Sara", "Thunder", "sara@example.com"),
            ("kyle.wolf", "Kyle", "Wolf", "kyle@example.com"),
            ("nina.flame", "Nina", "Flame", "nina@example.com"),
            ("dmitri.bear", "Dmitri", "Bear", "dmitri@example.com"),
            ("zara.lynx", "Zara", "Lynx", "zara@example.com"),
            ("ryan.hawk", "Ryan", "Hawk", "ryan@example.com"),
            ("eva.storm", "Eva", "Storm", "eva@example.com"),
        ]
        members = []
        for username, fn, ln, email in member_seed:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email, "first_name": fn, "last_name": ln,
                    "role": User.Role.MEMBER, "phone": f"+1 555 0{random.randint(100,999)} {random.randint(1000,9999)}",
                },
            )
            if created:
                u.set_password("spartan123")
                u.save()
            members.append(u)

        # ---- Plans ----
        if not Plan.objects.exists():
            Plan.objects.create(
                name="Recruit", tier=Plan.Tier.BASIC, price=Decimal("29"), duration_days=30,
                features="24/7 facility access\nUnlimited gym floor\nLocker room access\nFree water refill",
                color="#7dd3fc", icon="bi-lightning-charge",
            )
            Plan.objects.create(
                name="Hoplite", tier=Plan.Tier.STANDARD, price=Decimal("59"), duration_days=30,
                features="Everything in Recruit\nGroup classes (10/mo)\nFitness assessment\nGuest pass (2/mo)\nNutrition guide",
                color="#c8102e", icon="bi-shield-fill", is_featured=True,
            )
            Plan.objects.create(
                name="Warrior", tier=Plan.Tier.PREMIUM, price=Decimal("99"), duration_days=30,
                features="Everything in Hoplite\nUnlimited group classes\n2 PT sessions/mo\nMassage credits\nCustom meal plan\nSauna & steam",
                color="#ffb24c", icon="bi-trophy-fill",
            )
            Plan.objects.create(
                name="Spartan King", tier=Plan.Tier.ELITE, price=Decimal("199"), duration_days=30,
                features="Everything in Warrior\nUnlimited PT sessions\nPremium recovery zone\nDietitian consult\nVIP locker\nGuest passes (5/mo)",
                color="#a78bfa", icon="bi-gem",
            )
            self.stdout.write("Created 4 plans")

        plans_qs = list(Plan.objects.all())

        # ---- Trainers ----
        trainer_seed = [
            ("Achilles Vance", "Head Strength Coach", "Powerlifting · Olympic Lifting", 12),
            ("Andromeda Cole", "HIIT & Conditioning", "HIIT · Functional · Spartan Race", 8),
            ("Brutus Kane", "Combat Coach", "Boxing · Muay Thai · MMA", 15),
            ("Helena Rivera", "Yoga & Mobility", "Vinyasa · Mobility · Recovery", 9),
            ("Maximus Chen", "CrossFit Box Lead", "CrossFit · Gymnastics · Endurance", 11),
        ]
        trainers = []
        for name, title, spec, yrs in trainer_seed:
            t, _ = Trainer.objects.get_or_create(
                name=name,
                defaults={
                    "title": title, "specialty": spec, "years_experience": yrs,
                    "bio": f"{name} brings {yrs} years of competitive experience and elite-level coaching to every session. Trained nationally ranked athletes and weekend warriors alike.",
                },
            )
            trainers.append(t)

        # ---- Classes ----
        if not GymClass.objects.exists():
            class_seed = [
                ("Spartan Strength", "Heavy compound lifts and accessory work for raw power.", trainers[0], 0, time(7, 0), 60, "intermediate", "bi-lightning-charge", "#c8102e"),
                ("HIIT Inferno", "30-minute fat-melting metabolic conditioning.", trainers[1], 0, time(18, 0), 30, "all", "bi-fire", "#ffb24c"),
                ("Boxing Basics", "Footwork, fundamentals, and bag work.", trainers[2], 1, time(19, 0), 60, "beginner", "bi-trophy", "#7dd3fc"),
                ("Vinyasa Flow", "Movement, breath, and mobility for athletes.", trainers[3], 2, time(8, 30), 60, "all", "bi-heart-pulse", "#a78bfa"),
                ("CrossFit WOD", "Daily varied workout — leave your ego at the door.", trainers[4], 3, time(17, 30), 60, "advanced", "bi-activity", "#22c55e"),
                ("Spartan Bootcamp", "Drills, sprints, and team challenges outside.", trainers[1], 5, time(9, 0), 75, "all", "bi-flag", "#c8102e"),
                ("Olympic Lifting Lab", "Snatch and clean & jerk technique session.", trainers[0], 4, time(18, 30), 90, "intermediate", "bi-trophy-fill", "#ffb24c"),
                ("Recovery & Mobility", "Foam roll, stretch, breathwork. Heal the warrior.", trainers[3], 6, time(10, 0), 45, "all", "bi-heart", "#7dd3fc"),
            ]
            for name, desc, trainer, day, t, dur, lvl, icon, color in class_seed:
                GymClass.objects.create(
                    name=name, description=desc, trainer=trainer,
                    day_of_week=day, start_time=t, duration_minutes=dur,
                    capacity=20, level=lvl, icon=icon, color=color,
                )
            self.stdout.write("Created classes")

        # ---- Memberships + payments + attendance ----
        today = date.today()
        for m in members:
            if not m.memberships.exists():
                plan = random.choice(plans_qs)
                start = today - timedelta(days=random.randint(1, 60))
                ms = Membership.objects.create(
                    member=m, plan=plan, start_date=start,
                    end_date=start + timedelta(days=plan.duration_days),
                    status=Membership.Status.ACTIVE,
                )
                ms.refresh_status()
                ms.save()
                Payment.objects.create(
                    member=m, membership=ms, amount=plan.price,
                    method=random.choice([Payment.Method.CARD, Payment.Method.CASH, Payment.Method.UPI]),
                    status=Payment.Status.PAID,
                    paid_on=timezone.make_aware(datetime.combine(start, time(10, 30))),
                    note=f"Subscription to {plan.name}",
                )
            # attendance over last 14 days (random)
            if m.attendance_records.count() < 5:
                for _ in range(random.randint(3, 12)):
                    days_ago = random.randint(0, 13)
                    when = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 12))
                    Attendance.objects.create(member=m, check_in=when, note="Self check-in")

        # ---- Testimonials ----
        if not Testimonial.objects.exists():
            quotes = [
                ("Marcus Steel", "Member since 2024", 5,
                 "I lost 15kg and gained the confidence I'd been chasing for years. The coaches at Spartan don't just train you — they believe in you."),
                ("Helena Vance", "Member since 2023", 5,
                 "Walked in nervous, walked out a beast. The community here is unmatched. I look forward to every session."),
                ("Daniel Cross", "PT Client", 5,
                 "The personal training programs are next level. My deadlift went from 120 to 200kg in 9 months. Pure strength engineering."),
                ("Aria Petrov", "Yoga Member", 4,
                 "The yoga and mobility classes saved my back. I finally feel athletic again at 45. Coach Helena is a magician."),
                ("Tomás Rivera", "Boxing Member", 5,
                 "Coach Brutus is brutal in the best way. Sparring on Wednesdays is the highlight of my week. This place is electric."),
                ("Ines Morales", "Member since 2022", 5,
                 "I tried 3 gyms before Spartan. None of them came close. The energy, the equipment, the people — top tier."),
            ]
            for name, role, rating, q in quotes:
                Testimonial.objects.create(
                    author_name=name, author_role=role, rating=rating, quote=q,
                    is_published=True, is_featured=(rating == 5 and len(q) > 100),
                )

        # ---- Progress logs for "member" ----
        member_user = User.objects.get(username="member")
        if not member_user.progress_logs.exists():
            base_weight = 88
            for i in range(8, 0, -1):
                ProgressLog.objects.create(
                    member=member_user,
                    logged_on=today - timedelta(weeks=i),
                    weight_kg=Decimal(base_weight - (8 - i) * 0.7),
                    height_cm=Decimal("180"),
                    body_fat=Decimal(22 - (8 - i) * 0.4),
                )

        # ---- Sample contact messages ----
        if not ContactMessage.objects.exists():
            ContactMessage.objects.create(
                name="Jordan Reed", email="jordan@example.com",
                subject="Free trial?", message="Hi! I'd love to know if you offer a free trial week.",
            )
            ContactMessage.objects.create(
                name="Casey Wells", email="casey@example.com",
                subject="Corporate plans", message="Do you offer discounts for company memberships?",
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Seed complete!"))
        self.stdout.write("\nLogin credentials (all use password: spartan123)")
        self.stdout.write("  Super Admin → superadmin")
        self.stdout.write("  Admin (limited) → admin")
        self.stdout.write("  Member → member")
