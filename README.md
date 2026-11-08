# idiom-layered-animation

Claude Code skill：把成語故事做成「角色分層動畫網頁」。背景與角色分開，角色去背後疊在背景上，可以走進畫面、跳腳、換姿勢、說話時點頭、生氣時甩頭、嘴巴配合旁白開合；鏡頭每 2～3 秒剪接，加上推近、橫移與甩鏡。插圖用 Gemini 網頁版生成。

使用方式與完整流程見 [SKILL.md](SKILL.md)。只需要在整張插圖上推鏡頭時，請用 [idiom-scene-animation](https://github.com/kingvincentwang/idiom-scene-animation)。

## 安裝

```bash
git clone https://github.com/kingvincentwang/idiom-layered-animation.git ~/.claude/skills/idiom-layered-animation
```

需要 Python、Pillow、numpy、scipy。

## 內容

| 檔案 | 用途 |
|---|---|
| `assets/template.html` | 範本：〈朝三暮四〉分層版完整動畫（5 幕、換姿勢、頭部動作、口形、剪接、音效） |
| `scripts/cutout.py` | 去掉純白背景，輸出透明 PNG；可切出並排姿勢中的其中一個 |
| `scripts/split_head.py` | 把角色切成頭、身體兩層，讓頭可以點頭、甩頭（可把長鬍子歸到頭部） |
| `scripts/grid_crop.py` | 放大局部並加上格線，用來量脖子與嘴巴位置 |
| `scripts/check_layer_mouths.py` | 把每個姿勢的嘴巴以閉、半開、全開畫到圖上，拼成總覽檢查位置 |

範本不附圖層圖片；使用時在成語資料夾的 `layers/` 放入背景與角色圖。

## 注意

旁白使用瀏覽器內建語音，在不同電腦或瀏覽器播放時聲音可能不同。
