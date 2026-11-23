import asyncio
import os

import edge_tts

VOICE = "en-US-ChristopherNeural"  # Professional, confident tech voice

SCENES = {
    "scene_1_intro": (
        "Freelancers, consultants, and businesses constantly exchange invoices and contracts. "
        "But proving that a specific document existed in an exact state at a given date and time "
        "has historically required expensive third-party notaries or centralized registries you don't control. "
        "Today, we present Invoice Fingerprint Vault, a decentralized, tamper-proof proof-of-existence registry "
        "built on Gno.land."
    ),
    "scene_2_upload": (
        "Here in our web application, the user uploads their invoice. Notice that the sensitive invoice document "
        "never leaves the user's browser unhashed. "
        "Instead, a cryptographic SHA-256 fingerprint is calculated instantaneously in the client using the browser's "
        "native Web Crypto API. This 64-character hash uniquely identifies the document without exposing private "
        "financial details, client rates, or customer personally identifiable information."
    ),
    "scene_3_adena": (
        "With a single click, we invoke the Adena wallet. The user signs a transaction calling our deployed Gno realm "
        "on the onyx-1 testnet. "
        "The Gno realm immutably anchors the fingerprint, the submitter's wallet address, and the block timestamp "
        "directly into the Gno.land state tree. Once confirmed, we get a direct GnoScan explorer link verifying the "
        "on-chain inclusion."
    ),
    "scene_4_verify": (
        "Now, anyone can verify this invoice. Whether it's a client, an auditor, or a court, they can enter the "
        "fingerprint or simply drag and drop the original document into the public verification portal. "
        "Our backend queries the Gno testnet RPC via ABCI queries in real-time. If the document matches, it displays "
        "the verified proof of existence, the submitter's address, and the testnet block timestamp."
    ),
    "scene_5_closing": (
        "The entire smart contract is written in idiomatic Gno, leveraging Gno's deterministic execution and "
        "AVL tree storage. The off-chain vault provides clean user dashboards and instant querying. "
        "Next, we plan to support batch invoice timestamping and GRC-20 micro-payments for commercial registries. "
        "Thanks for watching!"
    )
}

async def generate_all():
    os.makedirs("media/audio", exist_ok=True)
    full_audio_files = []
    
    for scene_id, text in SCENES.items():
        out_path = f"media/audio/{scene_id}.mp3"
        print(f"Generating audio for {scene_id}...")
        communicate = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+0Hz")
        await communicate.save(out_path)
        print(f"Saved: {out_path}")
        full_audio_files.append(out_path)

    # Also generate one combined full narration file
    full_text = " ".join(SCENES.values())
    full_path = "media/audio/full_demo_narration.mp3"
    print("Generating complete continuous narration...")
    comm_full = edge_tts.Communicate(full_text, VOICE, rate="+0%", pitch="+0Hz")
    await comm_full.save(full_path)
    print(f"Saved full continuous narration: {full_path}")

if __name__ == "__main__":
    asyncio.run(generate_all())
