import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from database import db, register_db
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

    # Home / Dashboard
    @app.route('/')
    def index():
        # Fetch today's events for dashboard
        now = None  # optionally fetch datetime.datetime.now()
        events = list_events()  # use defaults or filter
        return render_template('index.html', events=events)

    # New Event form
    @app.route('/event/new', methods=['GET', 'POST'])
    def new_event():
        if request.method == 'POST':
            user_text = request.form['event_text']
            existing = list_events()
            result = schedule_event(user_text, existing, create_event)
            # result contains 'event' and 'prep_notes'
            flash('Event scheduled successfully!')
            return redirect(url_for('event_detail', event_id=result['event']['id']))
        return render_template('new_event.html')

    # Event detail + prep notes
    @app.route('/event/<event_id>')
    def event_detail(event_id):
        # You’d fetch from DB or call list_events to find the specific one
        return render_template('event_detail.html', event_id=event_id)

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
        events = list_events()
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

    return app


if __name__ == '__main__':
    create_app().run(debug=True)