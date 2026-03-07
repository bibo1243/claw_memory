#!/bin/bash
# Generate image for new goal: GTD
INPUT_IMG="/home/node/.openclaw/media/inbound/file_35---328d6458-bdfe-4fbe-a59e-6a1dc8af8adf.jpg"

echo "Generating for 完全掌握工作 (GTD 管理)..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) calmly organizing floating task bubbles into neat boxes labeled 'Inbox', 'Next', 'Waiting'. Zen-like focus, organized, efficient. Clean workspace background." goal_gtd.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_gtd.jpg" https://catbox.moe/user/api.php)

# Need to find the page ID first since it's newly created
# We can use a script to find ID by title, or just parse from previous output if we had it (we don't easily).
# Let's use a finder script.
PAGE_ID=$(python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_find_page_id.py "30a1fbf9-30df-811f-ae48-df0df29ad7f9" "完全掌握工作 (GTD 管理)")

if [ ! -z "$PAGE_ID" ]; then
    python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "$PAGE_ID" "Goal Image" "$URL"
    echo "Updated image for GTD goal."
else
    echo "Could not find page ID for GTD goal."
fi
