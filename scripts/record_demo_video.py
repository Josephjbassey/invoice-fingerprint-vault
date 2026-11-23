import os
import subprocess
import time

from playwright.sync_api import sync_playwright

RAW_VIDEO_DIR = "media/video_raw"
OUTPUT_VIDEO = "media/demo_video_gnome_vault.mp4"
AUDIO_TRACK = "media/audio/full_demo_narration.mp3"
SAMPLE_INVOICE = os.path.abspath("sample_invoices/invoice_apex_design_101.pdf")
FINGERPRINT = "53ed60e76da28e574e533a9dd80a8dc13012aafaee8652e488c0bb5287b54d4c"
ADENA_WALLET = "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2"

def record_walkthrough():
    os.makedirs(RAW_VIDEO_DIR, exist_ok=True)
    # Clear out any previous raw webm files
    for f in os.listdir(RAW_VIDEO_DIR):
        if f.endswith(".webm"):
            os.remove(os.path.join(RAW_VIDEO_DIR, f))

    print("Starting Playwright recording session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/usr/bin/chromium',
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            record_video_dir=RAW_VIDEO_DIR,
            record_video_size={'width': 1920, 'height': 1080},
            viewport={'width': 1920, 'height': 1080}
        )

        # Inject Adena wallet mock for seamless interaction
        context.add_init_script(f"""
            window.adena = {{
                AddEstablish: async (name) => {{ return {{ status: 'success' }}; }},
                AddEstablishConnection: async (name) => {{ return {{ status: 'success' }}; }},
                GetAccount: async () => {{
                    return {{
                        status: 'success',
                        data: {{ address: '{ADENA_WALLET}' }},
                        address: '{ADENA_WALLET}'
                    }};
                }},
                DoContract: async (tx) => {{
                    return {{
                        status: 'success',
                        data: {{
                            hash: '8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3',
                            height: '1350400'
                        }}
                    }};
                }}
            }};
        """)

        page = context.new_page()

        # Pre-authenticate via wallet-login API so session is established
        print("Authenticating session via Adena wallet...")
        page.goto("http://127.0.0.1:8000/verify/")
        page.evaluate(f"""
            fetch('/api/wallet-login/', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ address: '{ADENA_WALLET}' }})
            }});
        """)
        time.sleep(1)

        # -------------------------------------------------------------
        # SCENE 1: Introduction & The Problem (~25.5s)
        # -------------------------------------------------------------
        print("Recording Scene 1: Introduction & Problem...")
        page.goto("http://127.0.0.1:8000/static/demo_slides.html")
        time.sleep(5)
        # Smooth mouse hover over the invoice preview
        page.mouse.move(750, 420)
        time.sleep(4)
        page.mouse.move(850, 520)
        time.sleep(5)
        page.mouse.move(300, 480)
        time.sleep(6)
        page.mouse.move(500, 320)
        time.sleep(5.5)

        # -------------------------------------------------------------
        # SCENE 2: Upload & Instant Client-side Fingerprinting (~30s)
        # -------------------------------------------------------------
        print("Recording Scene 2: Upload & Instant Client-side Fingerprinting...")
        page.goto("http://127.0.0.1:8000/upload/")
        time.sleep(4)
        
        # Smooth mouse movement to the dropzone
        page.mouse.move(960, 400)
        time.sleep(2)
        
        # Set file input
        file_input = page.locator("#file-input")
        file_input.set_input_files(SAMPLE_INVOICE)
        time.sleep(3)

        # Move mouse over the calculated hash preview
        page.mouse.move(960, 490)
        time.sleep(5)
        page.mouse.move(960, 560)
        time.sleep(5)
        page.mouse.move(960, 680)
        time.sleep(11)

        # -------------------------------------------------------------
        # SCENE 3: Adena Wallet & On-Chain Anchoring (~24s)
        # -------------------------------------------------------------
        print("Recording Scene 3: Adena Wallet & On-Chain Anchoring...")
        adena_btn = page.locator("#adena-submit-btn")
        adena_btn.hover()
        time.sleep(2)
        adena_btn.click()
        
        # Wait for transition to success page
        page.wait_for_selector("h1:has-text('Document Registered!')", timeout=10000)
        time.sleep(4)
        
        # Hover over the registered certificate details
        page.mouse.move(960, 460)
        time.sleep(5)
        page.mouse.move(960, 560)
        time.sleep(5)
        page.mouse.move(800, 680)
        time.sleep(8)

        # -------------------------------------------------------------
        # SCENE 4: Public Verification Portal (~27s)
        # -------------------------------------------------------------
        print("Recording Scene 4: Public Verification Portal...")
        page.goto("http://127.0.0.1:8000/verify/")
        time.sleep(3)

        # Fill search input with the fingerprint
        search_input = page.locator("input[name='fingerprint']")
        search_input.click()
        time.sleep(1)
        search_input.fill(FINGERPRINT)
        time.sleep(3)

        # Click Verify button
        verify_btn = page.locator("button[type='submit']:has-text('Verify On-Chain')")
        verify_btn.hover()
        time.sleep(1)
        verify_btn.click()

        # Wait for verification result banner
        page.wait_for_selector("span:has-text('VERIFIED PROOF OF EXISTENCE')", timeout=10000)
        time.sleep(4)
        page.mouse.move(960, 500)
        time.sleep(6)
        page.mouse.move(960, 620)
        time.sleep(9)

        # -------------------------------------------------------------
        # SCENE 5: Dashboard & Architecture / Outro (~23s)
        # -------------------------------------------------------------
        print("Recording Scene 5: User Dashboard & Architecture...")
        page.goto("http://127.0.0.1:8000/dashboard/")
        time.sleep(6)
        page.mouse.move(960, 450)
        time.sleep(4)

        # Navigate to Architecture slide
        page.goto("http://127.0.0.1:8000/static/demo_architecture.html")
        time.sleep(6)
        page.mouse.move(500, 450)
        time.sleep(4)
        page.mouse.move(800, 550)
        time.sleep(3)

        print("Finished recording scenes. Closing browser...")
        context.close()
        browser.close()

    print("Browser closed. Raw recording saved.")

def mux_final_video():
    # Find recorded webm file
    webm_files = [f for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".webm")]
    if not webm_files:
        raise FileNotFoundError("No raw webm file found in RAW_VIDEO_DIR")
    
    raw_video = os.path.join(RAW_VIDEO_DIR, webm_files[0])
    print(f"Muxing {raw_video} with {AUDIO_TRACK} into {OUTPUT_VIDEO}...")

    cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", AUDIO_TRACK,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd, check=True)
    print(f"Successfully generated final demo video: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    record_walkthrough()
    mux_final_video()
