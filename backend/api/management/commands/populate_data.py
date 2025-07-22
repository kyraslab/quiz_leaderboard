import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from api.models import Quiz, QuizSession, Bidang


class Command(BaseCommand):
    help = 'Generate 10,000 users and 20,000 quiz sessions for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10000,
            help='Number of users to create (default: 10000)'
        )
        parser.add_argument(
            '--sessions',
            type=int,
            default=20000,
            help='Number of quiz sessions to create (default: 20000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before generating new data'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_sessions = options['sessions']
        
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            User.objects.all().delete()
            QuizSession.objects.all().delete()
            Quiz.objects.all().delete()

        self.stdout.write(f'Starting data generation...')
        self.stdout.write(f'Target: {num_users} users and {num_sessions} quiz sessions')

        if num_users <= 0 or num_sessions <= 0:
            self.stdout.write(self.style.ERROR('Both users and sessions must be greater than 0!'))
            return
        
        users = self.create_users(num_users)
        if not users:
            self.stdout.write(self.style.ERROR('No users created!'))
            return

        self.create_quizzes()
        if not Quiz.objects.exists():
            self.stdout.write(self.style.ERROR('No quizzes found! Create quizzes first.'))
            return
            
        self.create_quiz_sessions(users, num_sessions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {num_users} users and {num_sessions} quiz sessions!'
            )
        )

    def create_users(self, num_users):
        """Create users with realistic names"""
        self.stdout.write(f'Creating {num_users} users...')
        
        first_names = [
            'Adam', 'Ben', 'Claire', 'Diana', 'Evan', 'Faith', 'Gavin', 'Hannah',
            'Ian', 'Jack', 'Katherine', 'Laura', 'Mia', 'Noah', 'Owen', 'Paige',
            'Ryan', 'Sara', 'Tony', 'Uma', 'Vanessa', 'William', 'Xander', 'Yuri', 'Zoe',
            'Alice', 'Brian', 'Cameron', 'Danielle', 'Eva', 'Felix', 'Grace', 'Henry',
            'Isla', 'Joel', 'Katie', 'Lily', 'Megan', 'Nina', 'Oscar', 'Phoebe'
        ]
        
        last_names = [
            'Sanders', 'Williams', 'Kennedy', 'Smith', 'Parker', 'Lawson', 'Hayden',
            'Prescott', 'Nelson', 'Carson', 'Sampson', 'Monroe', 'Preston',
            'Wellington', 'Stevens', 'Andrews', 'Porter', 'Reynolds', 'Sullivan',
            'Ingram', 'Harrison', 'Stanford', 'Burton', 'Kingston', 'Pearson'
        ]
        
        users_data = []
        existing_usernames = set(User.objects.values_list('username', flat=True))
        
        for i in range(num_users):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            while True:
                first = first_name.lower()
                last = last_name.lower()
                number = random.randint(1, 999)
                username = f"{first}{last}{number}"
                
                if username not in existing_usernames:
                    existing_usernames.add(username)
                    break
            
            user = User(
                username=username,
                email=f"{username}@example.com",
                is_active=True
            )
            users_data.append(user)
            
            if (i + 1) % 1000 == 0:
                self.stdout.write(f'Prepared {i + 1}/{num_users} users...')
        
        with transaction.atomic():
            created_users = User.objects.bulk_create(users_data, batch_size=1000)
        
        self.stdout.write(f'Created {len(created_users)} users')
        
        return list(User.objects.filter(is_superuser=False, is_staff=False))
    
    def create_quizzes(self):
        """Create sample quizzes for each subject"""
        self.stdout.write('Creating sample quizzes...')
        
        quizzes_data = []
        base_date = timezone.now() - timedelta(days=30)
        
        for bidang_code, bidang_name in Bidang.choices:
            for i in range(random.randint(3, 5)):
                start_date = base_date + timedelta(days=random.randint(0, 25))
                end_date = start_date + timedelta(hours=random.randint(2, 48))
                
                quiz = Quiz(
                    title=f"{bidang_name} Quiz Week {i+1}",
                    bidang=bidang_code,
                    start_date=start_date,
                    end_date=end_date
                )
                quizzes_data.append(quiz)

        with transaction.atomic():
            Quiz.objects.bulk_create(quizzes_data, batch_size=1000)
        
        self.stdout.write(f'Created {len(quizzes_data)} quizzes')

    def create_quiz_sessions(self, users, num_sessions):
        """Create realistic quiz sessions ensuring one session per user per quiz"""
        self.stdout.write(f'Creating up to {num_sessions} quiz sessions...')
        
        quizzes = list(Quiz.objects.all())
        if not quizzes:
            self.stdout.write(self.style.ERROR('No quizzes found! Create quizzes first.'))
            return
        
        sessions_data = []
        created_combinations = set()
        attempts = 0
        max_attempts = num_sessions * 3
        
        while len(sessions_data) < num_sessions and attempts < max_attempts:
            user = random.choice(users)
            quiz = random.choice(quizzes)
            combination = (user.id, quiz.id)
            
            if combination in created_combinations:
                attempts += 1
                continue
                
            created_combinations.add(combination)
            score = random.randint(0, 100)

            quiz_duration = quiz.end_date - quiz.start_date
            max_start_offset = max(timedelta(0), quiz_duration - timedelta(hours=2))
            start_offset = timedelta(
                seconds=random.randint(0, int(max_start_offset.total_seconds()))
            )
            user_start = quiz.start_date + start_offset
            
            session_duration = timedelta(
                minutes=random.randint(5, 60)
            )
            user_end = user_start + session_duration
            
            if user_end > quiz.end_date:
                user_end = quiz.end_date
                session_duration = user_end - user_start
            
            session = QuizSession(
                user=user,
                quiz=quiz,
                score=score,
                duration=int(session_duration.total_seconds()),
                user_start=user_start,
                user_end=user_end
            )
            sessions_data.append(session)
            attempts += 1
            
            if len(sessions_data) % 2000 == 0:
                self.stdout.write(f'Prepared {len(sessions_data)}/{num_sessions} unique sessions...')
        
        if len(sessions_data) < num_sessions:
            self.stdout.write(
                self.style.WARNING(
                    f'Could only create {len(sessions_data)} unique sessions out of {num_sessions} requested'
                )
            )
        
        batch_size = 1000
        for i in range(0, len(sessions_data), batch_size):
            batch = sessions_data[i:i + batch_size]
            with transaction.atomic():
                QuizSession.objects.bulk_create(batch, batch_size=batch_size)
            self.stdout.write(f'Created batch {i//batch_size + 1}/{(len(sessions_data) + batch_size - 1)//batch_size}')
        
        self.stdout.write(f'Created {len(sessions_data)} quiz sessions')
