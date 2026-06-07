from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class ImageCardGenerator:
    def generate_summary_card(self, output_path: Path, title: str, lines: list[str]) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (1200, 630), color=(18, 24, 38))
        draw = ImageDraw.Draw(image)
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        draw.text((50, 50), title, fill=(255, 255, 255), font=font_title)
        y = 120
        for line in lines[:10]:
            draw.text((50, y), line, fill=(220, 230, 240), font=font_body)
            y += 48
        image.save(output_path)
        return output_path
