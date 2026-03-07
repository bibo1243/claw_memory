#!/bin/bash
# Generate images for all goals
# Requires: python3, GEMINI_API_KEY

# Reference image path
INPUT_IMG="/home/node/.openclaw/media/inbound/file_35---328d6458-bdfe-4fbe-a59e-6a1dc8af8adf.jpg"

# 1. AI軟體開發與閱讀
echo "Generating for AI軟體開發與閱讀..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) sitting on a stack of colorful books, typing on a futuristic laptop with holographic code floating around. Warm lighting, inspiring atmosphere." goal_ai_learning.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_ai_learning.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81e6-bf3a-e83a703d903f" "Goal Image" "$URL"

# 2. 戒色與意念淨化
echo "Generating for 戒色與意念淨化..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) meditating peacefully in a pure white and gold space, surrounded by a glowing shield protecting him from dark smoke. Zen, pure, clean energy." goal_purity.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_purity.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-812e-9c1c-e3639f41ecb3" "Goal Image" "$URL"

# 3. 掃地僧課程AI化與股市分析
echo "Generating for 掃地僧課程AI化與股市分析..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) analyzing a giant toy-like stock market chart with an AI robot assistant. Coins and graphs, playful but professional." goal_stock.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_stock.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-8128-b116-c80af8a43478" "Goal Image" "$URL"

# 4. 休閒旅遊計畫
echo "Generating for 休閒旅遊計畫..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) wearing a backpack and holding a camera, standing in a beautiful toy-like landscape with mountains and rivers (Guilin style). Relaxed, happy." goal_travel.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_travel.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-8154-b32c-cb28e33f3019" "Goal Image" "$URL"

# 5. 相聲短視頻挑戰
echo "Generating for 相聲短視頻挑戰..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) wearing a traditional Chinese gown (Changshan), holding a fan, performing on a stage with a microphone. Funny, lively expression." goal_challenge.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_challenge.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-8166-ab3f-f48850471b2e" "Goal Image" "$URL"

# 6. 健康生活作息
echo "Generating for 健康生活作息..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) sleeping peacefully in a cozy bed with a clock showing 23:00. Healthy food (vegetables) on a side table. Calm, restful." goal_health.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_health.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-8177-aaf7-c3240908811d" "Goal Image" "$URL"

# 7. 帶媽媽去金門廈門
echo "Generating for 帶媽媽去金門廈門..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) holding hands with an elderly lady (mother), walking happily near a traditional Kinmen style house. Warm family love." goal_mom.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_mom.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-819c-aa14-d2edf4407c9c" "Goal Image" "$URL"

# 8. 工作常規與督導
echo "Generating for 工作常規與督導..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) sitting at a neat desk, writing in a journal with a disciplined and focused expression. Organized office setting." goal_work_routine.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_work_routine.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81a3-a321-f6b859c509e7" "Goal Image" "$URL"

# 9. 協助爸爸畫畫與線上分享
echo "Generating for 協助爸爸畫畫與線上分享..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) helping an elderly man (father) who is painting on a canvas. Digital tablet nearby for online sharing. Artistic and supportive." goal_dad.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_dad.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81cb-8d66-ec370fe66b90" "Goal Image" "$URL"

# 10. 深度社交與AI推廣
echo "Generating for 深度社交與AI推廣..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) shaking hands with another person, with AI robot icons floating around them. Collaborative and friendly." goal_social.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_social.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81d1-84f0-c58892e1dc60" "Goal Image" "$URL"

# 11. 白銀出場策略
echo "Generating for 白銀出場策略..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) holding shiny silver bars, looking at a rising chart. Wealthy and smart investor vibe." goal_silver.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_silver.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81e8-87b9-d9c7402d4de3" "Goal Image" "$URL"

# 12. 專案業務完成
echo "Generating for 專案業務完成..."
GEMINI_API_KEY=$GEMINI_API_KEY python3 /home/node/.openclaw/workspace/skills/gemini-image-simple/scripts/generate.py "3D soft Q-version toy style. A cute asian man with glasses (based on input) checking off items on a big clipboard, celebrating success. Productive and accomplished." goal_project.jpg --input "$INPUT_IMG"
URL=$(curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@goal_project.jpg" https://catbox.moe/user/api.php)
python3 /home/node/.openclaw/workspace/skills/google-calendar/scripts/notion_update_image_prop.py "30c1fbf9-30df-81e8-9abc-d724356a8420" "Goal Image" "$URL"
