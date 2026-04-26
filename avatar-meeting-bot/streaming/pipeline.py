# streaming/pipeline.py
import threading
from core.stt        import SpeechToText
from core.tts        import VoiceCloner
from core.avatar     import AvatarGenerator
from core.llm_client import LLMClient
from streaming.virtual_cam import VirtualCamera


class MeetingPipeline:
    def __init__(self):
        print("\n" + "="*55)
        print("   AVATAR MEETING BOT — INITIALIZING")
        print("="*55)

        self.stt    = SpeechToText()
        self.tts    = VoiceCloner()
        self.avatar = AvatarGenerator()
        self.llm    = LLMClient()
        self.cam    = VirtualCamera()

        # Show face photo immediately in OBS window
        self.cam.show_idle()

        print("\n✅ All systems ready")
        print("="*55 + "\n")

    def process(self, question):
        """
        Full pipeline for one question:
        question text → LLM answer → voice audio → avatar video → stream
        """
        print(f"\n[PIPELINE] Processing: '{question}'")

        # Show idle photo while generating response
        self.cam.show_idle()

        # Step 1: Get answer from Member A's LLM
        answer = self.llm.ask(question)

        # Step 2: Generate cloned voice audio
        audio_path = self.tts.generate(answer)
        if not audio_path:
            print("[PIPELINE] TTS failed — skipping this turn")
            return

        # Step 3: Play audio immediately (don't wait for video)
        audio_thread = threading.Thread(
            target=self.cam.play_audio,
            args=(audio_path,)
        )
        audio_thread.start()

        # Step 4: Generate avatar video (runs while audio plays)
        video_path = self.avatar.generate(audio_path)

        # Step 5: Wait for audio to finish, then play video
        audio_thread.join()
        if video_path:
            self.cam.play_video(video_path)
        else:
            print("[PIPELINE] Avatar generation failed — audio only")

    def run(self):
        """Main loop — listens continuously to meeting audio"""
        print("🎙️  Listening to meeting...")
        print("    Speak into your mic to trigger a response")
        print("    Press Ctrl+C to stop the bot\n")

        while True:
            try:
                question = self.stt.listen_and_transcribe()

                # Ignore silence or very short sounds
                if question and len(question) > 5:
                    self.process(question)

            except KeyboardInterrupt:
                print("\n[STOP] Bot stopped.")
                break

            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                print("[INFO] Continuing to listen...")
                continue
