
# Avatar Training SaaS（Azure TTS フル版）

- **フロント**: `frontend/index.html`（GitHub Pagesで公開OK）
- **バックエンド**: FastAPI（Whisper STT / **Azure TTS** / OpenAI互換LLM）
- **データ**: 行政ルーブリックv1 + “迷惑IT”シナリオ5本

## クラウド公開（ローカル不要）
1) GitHubに新規Repo → このフォルダ一式をアップ  
2) RenderでWeb Service作成（`deploy/render.yaml` 参照）  
   - 必須ENV: `OPENAI_API_KEY`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`  
3) GitHub Pages → Branch: `main`, Folder: `/frontend`  
4) PagesのURLに `?api=RenderのURL` を付けてアクセス

## 動作
- 左：**長押し録音→離す**で送信 → Azureの合成音が再生（2Dアバター口パク）
- 右：テキスト入力→**送信**、**採点**ボタンでスコア表示

## 設定項目
- LLM: `OPENAI_*` 環境変数（Azure OpenAI/ローカル互換APIも可）
- TTS: `AZURE_SPEECH_*`（VOICEの候補: `ja-JP-NanamiNeural`, `ja-JP-KeitaNeural` など）
- シナリオ: `backend/data/scenarios_it.json`
- ルーブリック: `backend/data/rubric_basic.json`

## API概要
- `POST /session/hear_audio` : 音声→STT→LLM→TTS（WAV base64）
- `POST /session/hear` : テキスト→LLM返答
- `POST /score/evaluate` : ルール+LLMで採点

Happy shipping 🎉
