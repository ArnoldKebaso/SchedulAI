import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from database import db, register_db
from database.models import EventCache
from calendar_module.calendar_service import list_events, create_event
from ai.scheduler_ai import schedule_event


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', app.config['SQLALCHEMY_DATABASE_URI']
    )

    # Initialize DB
    register_db(app)
    Migrate(app, db)
    
    # Create tables
    with app.app_context():
        db.create_all()

    # Home / Dashboard
    @app.route('/')
    def index():
        # Fetch today's events for dashboard
        # Try Google Calendar first, fallback to local database
        events = list_events()
        if not events:
            # Get events from local database
            db_events = EventCache.query.all()
            events = [
                {
                    'summary': event.summary,
                    'start': event.start,
                    'end': event.end,
                    'id': event.id
                }
                for event in db_events
            ]
        return render_template('index.html', events=events)

    # New Event form
    @app.route('/event/new', methods=['GET', 'POST'])
    def new_event():
        if request.method == 'POST':
            user_text = request.form['event_text']
            existing = list_events()
            
            # Create a wrapper function that saves to both Google Calendar and local DB
            def create_event_with_fallback(event_data):
                try:
                    # Try Google Calendar first
                    google_event = create_event(event_data)
                    event_id = google_event.get('id', str(uuid.uuid4()))
                except Exception as e:
                    print(f"Google Calendar failed, using local storage: {e}")
                    event_id = str(uuid.uuid4())
                
                # Always save to local database
                local_event = EventCache(
                    id=event_id,
                    summary=event_data.get('summary', 'New Event'),
                    start=event_data.get('start'),
                    end=event_data.get('end')
                )
                db.session.add(local_event)
                db.session.commit()
                
                return {
                    'id': event_id,
                    'summary': event_data.get('summary', 'New Event'),
                    'start': event_data.get('start'),
                    'end': event_data.get('end')
                }
            
            result = schedule_event(user_text, existing, create_event_with_fallback)
            # result contains 'event' and 'prep_notes'
            flash('Event scheduled successfully!')
            return redirect(url_for('event_detail', event_id=result['event']['id']))
        return render_template('new_event.html')

    # Event detail + prep notes
    @app.route('/event/<event_id>')
    def event_detail(event_id):
        # Try to get event from local database first
        local_event = EventCache.query.get(event_id)
        if local_event:
            event = {
                'id': local_event.id,
                'summary': local_event.summary,
                'start': local_event.start,
                'end': local_event.end
            }
        else:
            # Fallback to dummy event if not found
            event = {
                'id': event_id,
                'summary': f'Event {event_id}',
                'start': '2025-07-27T10:00:00',
                'end': '2025-07-27T11:00:00'
            }
        
        prep_notes = f"Preparation notes for: {event['summary']}"
        return render_template('event_detail.html', event=event, prep_notes=prep_notes)

    # Conflict resolution page (if you want separate route)
    @app.route('/conflicts')
    def conflicts():
        return render_template('conflict_resolution.html')

    # Follow-ups
    @app.route('/followups')
    def followups():
        return render_template('followups.html')
    
    # Calendar view
    @app.route('/calendar')
    def calendar():
        # Try Google Calendar first, fallback to local database
        events = list_events()
        if not events:
            # Get events from local database
            db_events = EventCache.query.all()
            events = [
                {
                    'summary': event.summary,
                    'start': event.start,
                    'end': event.end,
                    'id': event.id
                }
                for event in db_events
            ]
        return render_template('calendar.html', events=events)
    
    # Test AI endpoint
    @app.route('/test-ai')
    def test_ai():
        from ai.scheduler_ai import chat, parse_event
        try:
            # Test basic chat
            response = chat("Say hello briefly")
            
            # Test event parsing
            test_event = parse_event("Meeting with John tomorrow at 2 PM for 1 hour")
            
            return f"<h1>AI Test Results</h1><h2>Chat Response:</h2><p>{response}</p><h2>Parsed Event:</h2><pre>{test_event}</pre>"
        except Exception as e:
            return f"<h1>AI Test Error</h1><p>{str(e)}</p>"
    
    # Debug route to see all events in database
    @app.route('/debug/events')
    def debug_events():
        db_events = EventCache.query.all()
        events_html = "<h1>Events in Database</h1><ul>"
        for event in db_events:
            events_html += f"<li><strong>{event.summary}</strong> - {event.start} to {event.end} (ID: {event.id})</li>"
        events_html += "</ul>"
        events_html += f"<p>Total events: {len(db_events)}</p>"
        events_html += "<a href='/'>Back to Dashboard</a>"
        return events_html

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
