from flask import Flask, request
from markupsafe import Markup
import traceback
from youtube import YouTube
from dataclass.publication import Publication
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task

app = Flask(__name__)

youtube = YouTube()

@CrewBase
class YoutubeSponsorshipDetector():
    """YoutubeSponsorshipDetector crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def sponsorship_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['sponsorship_detector'],
            verbose=True, 
        )
    
    @task
    def sponsorship_detecting_task(self) -> Task:
        return Task(
            config=self.tasks_config['sponsorship_detecting_task'],
            verbose=True
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  
            tasks=self.tasks,    
            process=Process.sequential,
            verbose=True,
        )

@app.route('/')
def home():
    YoutubeSponsorshipDetector().crew().kickoff(inputs={
        "description": "@nala.money - sure update for FX transfer this period and beyond. Download @nala.money app with my code SABINUS. Use to send love home and get the “investor”.",
    })
    return "Hello, Flask!"

@app.route('/channels', methods=['GET'])
def confirm_channel_subscription():
    channel_id = request.args.get('hub.topic').split("channel_id=")[1]
    lease_seconds = request.args.get('hub.lease_seconds')
    challenge = request.args.get('hub.challenge')
    challenge_escaped = str(Markup.escape(challenge))
    return challenge_escaped

@app.route('/channels', methods=['POST'])
def detect_publication():
    doc = request.data.decode('utf-8')
    try:
        publication = Publication.from_xml(doc)
        result = youtube.get_videos(publication.id)
        description = result['items'][0]['snippet']['description']
        publication.description = description

        YoutubeSponsorshipDetector().crew().kickoff(inputs={"description": publication.description})
    except Exception:
        print(traceback.format_exc())
        return "exception", 500

    return "", 200

@app.route('/youtube-publications', methods=['GET'])
def publications():
    publication_ids = request.args.get('publication_ids')
    result = youtube.get_videos(publication_ids)
    return result, 200

if __name__ == "__main__":
    app.run(debug=True)
