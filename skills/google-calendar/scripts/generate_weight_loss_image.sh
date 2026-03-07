#!/bin/bash
# Generate image for new goal: Weight Loss
INPUT_IMG="/home/node/.openclaw/media/inbound/file_35---328d6458-bdfe-4fbe-a59e-6a1dc8af8adf.jpg"

echo "Generating for 體態雕塑：80kg → 74kg (減重 6kg)..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) standing on a scale, looking happy and fit. Wearing sportswear, holding a water bottle. Background shows a downward trend chart. Healthy, energetic." goal_weight_loss.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_weight_loss.jpg" https://catbox.moe/user/api.php)

PAGE_ID=$(python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_find_page_id.py "30a1fbf9-30df-811f-ae48-df0df29ad7f9" "體態雕塑：80kg → 74kg (減重 6kg)")

if [ ! -z "$PAGE_ID" ]; then
    python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "$PAGE_ID" "Goal Image" "$URL"
    echo "Updated image for Weight Loss goal."
else
    echo "Could not find page ID for Weight Loss goal."
fi
