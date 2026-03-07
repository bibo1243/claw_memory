#!/bin/bash
# Generate image for Daily Improvement Day 802
INPUT_IMG="/home/node/.openclaw/media/inbound/file_35---328d6458-bdfe-4fbe-a59e-6a1dc8af8adf.jpg"

echo "Generating for 日精進 Day 802：AI 能量注入與維次提升..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) floating in a higher dimension, surrounded by glowing digital orbs (AI energy). Below him are small figures busy with repetitive tasks, but he looks calm and enlightened, holding a 'Life' heart symbol. Magical, futuristic but warm." diary_day_802.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@diary_day_802.jpg" https://catbox.moe/user/api.php)

# Need to find page ID first.
PAGE_ID=$(python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_find_page_id.py "30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2" "日精進 Day 802：AI 能量注入與維次提升")

if [ ! -z "$PAGE_ID" ]; then
    # For Tasks database, we use 'Photo' property, not 'Goal Image'
    python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "$PAGE_ID" "Photo" "$URL"
    echo "Updated image for Diary Day 802."
else
    echo "Could not find page ID for Diary Day 802."
fi
