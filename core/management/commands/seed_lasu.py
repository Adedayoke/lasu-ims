import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Department, AssetCategory, Asset

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed LASU IMS with initial departments, users, categories, and sample assets'

    def handle(self, *args, **options):
        self.stdout.write('Seeding LASU IMS database…')

        # 1. Departments
        dept_data = [
            ('Engineering', 'ENG', 'Faculty of Engineering'),
            ('Sciences', 'SCI', 'Faculty of Sciences'),
            ('Administration', 'ADMIN', 'Central Administration'),
            ('Library', 'LIB', 'University Library'),
            ('ICT Unit', 'ICT', 'Information & Communications Technology'),
        ]
        depts = {}
        for name, code, faculty in dept_data:
            dept, created = Department.objects.get_or_create(code=code, defaults={'name': name, 'faculty': faculty})
            depts[code] = dept
            if created:
                self.stdout.write(f'  Created department: {name}')

        # 2. Asset Categories
        cat_data = [
            ('Computers & Laptops', 'Desktop computers, laptops, workstations', Decimal('20.00')),
            ('Furniture', 'Tables, chairs, shelves, filing cabinets', Decimal('5.00')),
            ('Lab Equipment', 'Scientific instruments and lab gear', Decimal('15.00')),
            ('Networking Equipment', 'Switches, routers, access points, cables', Decimal('25.00')),
            ('Printers & Scanners', 'Laser printers, scanners, photocopiers', Decimal('20.00')),
            ('Audio/Visual Equipment', 'Projectors, screens, speakers, cameras', Decimal('15.00')),
            ('Power Equipment', 'Generators, UPS, inverters, stabilizers', Decimal('10.00')),
            ('Office Equipment', 'Phones, calculators, shredders, safes', Decimal('10.00')),
            ('Library Resources', 'Bookshelves, reading tables, lockers', Decimal('5.00')),
            ('HVAC Equipment', 'Air conditioners, fans, ventilation units', Decimal('15.00')),
        ]
        cats = {}
        for name, desc, dep_rate in cat_data:
            cat, created = AssetCategory.objects.get_or_create(name=name, defaults={'description': desc, 'depreciation_rate': dep_rate})
            cats[name] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

        # 3. Create superadmin
        superadmin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@lasu.edu.ng',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'superadmin',
                'must_change_password': True,
                'is_staff': True,
                'is_superuser': True,
                'staff_id': 'LASU-SA-001',
            }
        )
        if created:
            superadmin.set_password('Admin@1234')
            superadmin.save()
            self.stdout.write(self.style.SUCCESS('  Created superadmin: admin@lasu.edu.ng / Admin@1234'))

        # 4. Test users per role
        test_users = [
            ('store_officer', 'storekeeper', 'Bode', 'Adeyemi', 'store@lasu.edu.ng', 'LASU-SO-001', depts['ADMIN']),
            ('hod', 'hod_eng', 'Prof. Emeka', 'Okafor', 'hod@lasu.edu.ng', 'LASU-HOD-001', depts['ENG']),
            ('auditor', 'auditor1', 'Amaka', 'Nwosu', 'auditor@lasu.edu.ng', 'LASU-AUD-001', None),
            ('bursar', 'bursar1', 'Tunde', 'Fashola', 'bursar@lasu.edu.ng', 'LASU-BUR-001', None),
        ]
        for role, username, first, last, email, staff_id, dept in test_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'department': dept,
                    'staff_id': staff_id,
                    'must_change_password': False,
                }
            )
            if created:
                user.set_password('Test@1234')
                user.save()
                self.stdout.write(f'  Created {role}: {username} / Test@1234')

        # Link HOD to engineering department
        hod_user = User.objects.filter(username='hod_eng').first()
        if hod_user:
            depts['ENG'].hod = hod_user
            depts['ENG'].save()

        # 5. Sample assets
        asset_templates = [
            ('Dell Inspiron Laptop', 'Computers & Laptops', 'ICT', 'new', Decimal('350000')),
            ('HP LaserJet Printer', 'Printers & Scanners', 'ADMIN', 'good', Decimal('180000')),
            ('Cisco Catalyst Switch', 'Networking Equipment', 'ICT', 'good', Decimal('520000')),
            ('Laboratory Centrifuge', 'Lab Equipment', 'SCI', 'good', Decimal('450000')),
            ('Office Chair (Executive)', 'Furniture', 'ADMIN', 'good', Decimal('45000')),
            ('Epson Projector', 'Audio/Visual Equipment', 'ENG', 'good', Decimal('220000')),
            ('Thermodynamics Textbooks (Set)', 'Library Resources', 'LIB', 'fair', Decimal('85000')),
            ('APC Smart-UPS 3000VA', 'Power Equipment', 'ICT', 'good', Decimal('195000')),
            ('Samsung Split AC 2HP', 'HVAC Equipment', 'ADMIN', 'good', Decimal('320000')),
            ('Canon Photocopier', 'Printers & Scanners', 'LIB', 'fair', Decimal('280000')),
            ('HP Desktop Computer', 'Computers & Laptops', 'ENG', 'good', Decimal('320000')),
            ('Steel Filing Cabinet', 'Furniture', 'ADMIN', 'good', Decimal('35000')),
            ('Lenovo ThinkPad', 'Computers & Laptops', 'SCI', 'new', Decimal('480000')),
            ('Oscilloscope Tektronix', 'Lab Equipment', 'ENG', 'good', Decimal('680000')),
            ('Mikrotik Router', 'Networking Equipment', 'ICT', 'good', Decimal('75000')),
            ('Conference Table (12-seater)', 'Furniture', 'ADMIN', 'good', Decimal('250000')),
            ('Panasonic IP Phone', 'Office Equipment', 'ADMIN', 'good', Decimal('28000')),
            ('Generator 50KVA (Mikano)', 'Power Equipment', 'ADMIN', 'good', Decimal('3500000')),
            ('Whiteboard (Interactive)', 'Audio/Visual Equipment', 'ENG', 'new', Decimal('380000')),
            ('Dell PowerEdge Server', 'Computers & Laptops', 'ICT', 'good', Decimal('1200000')),
        ]

        store_officer = User.objects.filter(username='admin').first()
        created_count = 0
        for name, cat_name, dept_code, condition, cost in asset_templates:
            if Asset.objects.filter(name=name).exists():
                continue
            purchase_date = date.today() - timedelta(days=random.randint(30, 730))
            asset = Asset(
                name=name,
                category=cats[cat_name],
                department=depts[dept_code],
                status='in_store',
                condition=condition,
                purchase_date=purchase_date,
                purchase_cost=cost,
                supplier_name=random.choice(['Lagos Supplies Ltd', 'TechHub Nigeria', 'ICS Technology', 'Zinox Distribution', 'Microlinks ICT']),
                location_description=f'{depts[dept_code].name} — Store',
                created_by=store_officer,
            )
            asset.save()
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} sample assets'))
        self.stdout.write(self.style.SUCCESS('\nSeed complete! You can now login at /login/ with:'))
        self.stdout.write('  Superadmin:    admin / Admin@1234')
        self.stdout.write('  Store Officer: storekeeper / Test@1234')
        self.stdout.write('  HOD:           hod_eng / Test@1234')
        self.stdout.write('  Auditor:       auditor1 / Test@1234')
        self.stdout.write('  Bursar:        bursar1 / Test@1234')
