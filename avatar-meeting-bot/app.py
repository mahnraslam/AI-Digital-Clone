# app.py — Main entry point
# Run this to start the avatar meeting bot:
#   conda activate ai-clone
#   cd C:\Users\Administrator\avatar-meeting-bot
#   python app.py

from streaming.pipeline import MeetingPipeline


if __name__ == "__main__":
    bot = MeetingPipeline()
    bot.run()
