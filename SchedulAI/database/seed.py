from database import db
from database.models import User, EventCache, FollowUpTask
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed():
    # Create a demo user
    demo = User(
        username='demo',
        password_hash=generate_password_hash('password123')
    )
    db.session.add(demo)

    # Create some sample events in cache
    now = datetime.utcnow()
    sample_event = EventCache(
        id='evt1',
        summary='Demo Meeting',
        start=(now + timedelta(hours=1)).isoformat(),
        end=(now + timedelta(hours=2)).isoformat(),
    )
    db.session.add(sample_event)

    # Sample follow-up
    follow = FollowUpTask(
        event_id='evt1',
        followup_date=now + timedelta(days=1)
    )
    db.session.add(follow)

    db.session.commit()
    print("Database seeded with demo data.")


if __name__ == '__main__':
    seed()