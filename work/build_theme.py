from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
THEME = WORK / "kurimanjyu-ios-theme"
IMAGES = THEME / "Images"
SOURCE = WORK / "source-images"
OUTPUTS = ROOT / "outputs"

THEME_NAME = "Kurimanjyu Chic"
PACKAGE_NAME = "kurimanjyu-chic.ktheme"

CREAM = "#F8EEDC"
CREAM_2 = "#FFF8EC"
BROWN = "#6B4A32"
BROWN_DARK = "#3E2A1F"
BROWN_LIGHT = "#A9774F"
SEND = "#D6A96F"
RECEIVE = "#FFF4DE"
LINE = "#7A563B"
PROFILE_SOURCES = ["kya.jpg", "kya3.jpg", "kuri-snack.webp", "kuri-drink.webp", "kya2.png", "kuri-bath.webp", "kuri-hangover.webp"]
TAB_SOURCES = {
    "friends": PROFILE_SOURCES[0],
    "chats": PROFILE_SOURCES[1],
    "browse": PROFILE_SOURCES[2],
    "find": PROFILE_SOURCES[2],
    "piccoma": PROFILE_SOURCES[3],
    "game": PROFILE_SOURCES[3],
    "more": PROFILE_SOURCES[4],
    "openchats": PROFILE_SOURCES[2],
    "shopping": PROFILE_SOURCES[3],
}


def load_portrait(source: str) -> Image.Image:
    image = load_image(source)
    bounds = {
        "kya.jpg": (0.20, 0, 1, 1),
        "kya3.jpg": (0, 0, 1, 1),
        "kuri-snack.webp": (0.24, 0.04, 0.68, 0.92),
        "kuri-drink.webp": (0.16, 0.02, 0.66, 0.95),
        "kya2.png": (0.42, 0, 1, 1),
        "kuri-bath.webp": (0, 0.18, 0.50, 0.94),
        "kuri-hangover.webp": (0, 0, 1, 1),
    }[source]
    return image.crop(tuple(round(value * (image.width if index % 2 == 0 else image.height)) for index, value in enumerate(bounds)))


def load_image(name: str) -> Image.Image:
    img = Image.open(SOURCE / name)
    if getattr(img, "is_animated", False):
        img.seek(0)
    return img.convert("RGBA")


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def circle_crop(img: Image.Image, size: int) -> Image.Image:
    fitted = fit_cover(img, (size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(fitted, (0, 0), mask)
    return out


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, scale: int) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + 112 * scale, y + 28 * scale), radius=14 * scale, fill="#F1D9B9")
    draw.text((x + 14 * scale, y + 6 * scale), text, fill=BROWN_DARK)


def make_wallpaper(size: tuple[int, int], scale: int, *, chat: bool) -> Image.Image:
    base = Image.new("RGBA", size, CREAM if chat else CREAM_2)
    draw = ImageDraw.Draw(base)
    w, h = size

    for y in range(-80 * scale, h, 160 * scale):
        for x in range(-80 * scale, w, 160 * scale):
            fill = "#F2DDC2" if (x // (160 * scale) + y // (160 * scale)) % 2 else "#FAF0DF"
            draw.ellipse((x, y, x + 44 * scale, y + 44 * scale), fill=fill)

    imgs = [
        load_image("kya.jpg"),
        load_image("kya2.png"),
        load_image("kya3.jpg"),
        load_image("kurimanjyu-eating.gif"),
    ]
    placements = [
        (0.05, 0.09, 0.42, -8),
        (0.56, 0.18, 0.36, 7),
        (0.08, 0.53, 0.34, 5),
        (0.54, 0.66, 0.39, -5),
    ]
    if not chat:
        placements = [(0.58, 0.08, 0.32, 3), (0.08, 0.58, 0.28, -4)]
        imgs = [imgs[2], imgs[1]]

    for img, (px, py, pw, angle) in zip(imgs, placements):
        tile_w = int(w * pw)
        tile_h = int(tile_w * 0.78)
        tile = fit_cover(img, (tile_w, tile_h))
        tile = ImageEnhance.Color(tile).enhance(0.92)
        card = Image.new("RGBA", (tile_w + 16 * scale, tile_h + 16 * scale), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card)
        card_draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=22 * scale, fill="#FFF9EF")
        card_draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=22 * scale, outline="#C49A73", width=max(1, 2 * scale))
        card.paste(tile, (8 * scale, 8 * scale), rounded_mask(tile.size, 16 * scale))
        card = card.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        card.putalpha(ImageEnhance.Brightness(card.getchannel("A")).enhance(0.72 if chat else 0.55))
        base.alpha_composite(card, (int(w * px), int(h * py)))

    if chat:
        draw_label(draw, (28 * scale, 34 * scale), "Kuri", scale)
        draw_label(draw, (w - 144 * scale, h - 74 * scale), "Chic", scale)

    shade = Image.new("RGBA", size, (255, 248, 236, 90 if chat else 135))
    base = Image.alpha_composite(base, shade)
    return base.convert("RGB")


def save_scaled(name: str, logical_size: tuple[int, int], factory) -> None:
    for suffix, scale in [("@2x", 2), ("@3x", 3)]:
        img = factory((logical_size[0] * scale, logical_size[1] * scale), scale)
        img.save(IMAGES / f"{name}{suffix}.png")
    factory((logical_size[0] * 2, logical_size[1] * 2), 2).save(IMAGES / f"{name}.png")


def make_bubble(size: tuple[int, int], scale: int, *, send: bool, selected: bool, grouped: bool = False) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    body = "#AEBCA0" if not selected else "#98A88A"

    left = 6 * scale
    right = w - 6 * scale
    top = 2 * scale
    bottom = h - 2 * scale

    draw.rounded_rectangle((left, top, right, bottom), radius=12 * scale, fill=body)
    if not grouped:
        if send:
            points = [(right - 7 * scale, top + 2 * scale), (w - scale, top + 2 * scale), (right - scale, top + 12 * scale)]
        else:
            points = [(left + 7 * scale, top + 2 * scale), (scale, top + 2 * scale), (left + scale, top + 12 * scale)]
        draw.polygon(points, fill=body)
    return img


def save_bubble(name: str, send: bool, selected: bool) -> None:
    for suffix, scale in [("@2x", 2), ("@3x", 3)]:
        make_bubble((104 * scale, 54 * scale), scale, send=send, selected=selected, grouped="02" in name).save(IMAGES / f"{name}{suffix}.png")
    make_bubble((208, 108), 2, send=send, selected=selected, grouped="02" in name).save(IMAGES / f"{name}.png")


def make_theme_icon() -> None:
    src = load_image("kya3.jpg")
    icon = Image.new("RGBA", (162, 162), CREAM)
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((0, 0, 161, 161), radius=34, fill=CREAM)
    draw.ellipse((17, 17, 145, 145), fill="#E6BE84")
    face = circle_crop(src, 118)
    icon.alpha_composite(face, (22, 24))
    draw.rounded_rectangle((17, 118, 145, 150), radius=16, fill="#3E2A1FCC")
    draw.text((45, 126), "KURI", fill="#FFF4DE")
    icon.convert("RGBA").save(IMAGES / "commonIcoTheme.png")


def make_profiles() -> None:
    for idx, source in enumerate(PROFILE_SOURCES, start=1):
        for suffix, size in [("", 160), ("@2x", 160), ("@3x", 240)]:
            profile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(profile)
            draw.ellipse((0, 0, size - 1, size - 1), fill="#F3D5AA")
            crop = circle_crop(load_portrait(source), int(size * 0.88))
            profile.alpha_composite(crop, (int(size * 0.06), int(size * 0.06)))
            draw.ellipse((0, 0, size - 1, size - 1), outline=LINE, width=max(2, size // 60))
            profile.save(IMAGES / f"profileImg{idx:02d}{suffix}.png")


def face_thumbnail(source: str, size: int, *, selected: bool = False, portrait: bool = False) -> Image.Image:
    pad = max(2, size // 14)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ring = "#6B4A32" if selected else "#D7B37D"
    draw.ellipse((0, 0, size - 1, size - 1), fill="#F9D48D", outline=ring, width=max(2, size // 18))
    crop = circle_crop(load_portrait(source) if portrait else load_image(source), size - pad * 2)
    img.alpha_composite(crop, (pad, pad))
    if selected:
        draw.ellipse((2, 2, size - 3, size - 3), outline="#FFF8EC", width=max(1, size // 30))
    return img


def draw_tab_icon(kind: str, selected: bool, size: tuple[int, int], scale: int) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    face_size = int(min(w, h) * (0.86 if selected else 0.78))
    face = face_thumbnail(TAB_SOURCES[kind], face_size, selected=selected, portrait=True)
    img.alpha_composite(face, (cx - face_size // 2, cy - face_size // 2))
    if selected:
        draw.rounded_rectangle((cx - 17 * scale, h - 5 * scale, cx + 17 * scale, h - 1 * scale), radius=2 * scale, fill=BROWN_DARK)
    return img


def make_passcode_assets() -> None:
    sources = ["kya3.jpg", "kya.jpg", "kya2.png", "kurimanjyu-eating.gif"]
    for idx, source in enumerate(sources, start=1):
        for selected, selected_name in [(False, ""), (True, "Selected")]:
            for suffix, scale in [("", 2), ("@2x", 2), ("@3x", 3)]:
                size = 28 * scale
                icon = face_thumbnail(source, size, selected=selected)
                if not selected:
                    icon.putalpha(ImageEnhance.Brightness(icon.getchannel("A")).enhance(0.72))
                icon.save(IMAGES / f"passcodeImgCode{idx:02d}{selected_name}{suffix}.png")
    for suffix, scale in [("", 2), ("@2x", 2), ("@3x", 3)]:
        press = Image.new("RGBA", (54 * scale, 54 * scale), (0, 0, 0, 0))
        draw = ImageDraw.Draw(press)
        draw.ellipse((4 * scale, 4 * scale, 50 * scale, 50 * scale), fill="#E5C49499")
        press.save(IMAGES / f"passcodeKeypadPressed{suffix}.png")


def make_tab_assets() -> None:
    for kind in TAB_SOURCES:
        asset = {
            "friends": "Friends",
            "chats": "Chats",
            "browse": "Browse",
            "find": "Find",
            "piccoma": "Piccoma",
            "game": "Game",
            "more": "More",
            "openchats": "OpenChats",
            "shopping": "Shopping",
        }[kind]
        for selected, postfix in [(False, ""), (True, "Selected")]:
            for suffix, scale in [("@2x", 2), ("@3x", 3)]:
                draw_tab_icon(kind, selected, (48 * scale, 48 * scale), scale).save(IMAGES / f"maintabIco{asset}{postfix}{suffix}.png")
            draw_tab_icon(kind, selected, (96, 96), 2).save(IMAGES / f"maintabIco{asset}{postfix}.png")


def make_extra_assets() -> None:
    save_scaled("chatroomBgImage", (393, 852), lambda size, scale: make_wallpaper(size, scale, chat=True))
    save_scaled("mainBgImage", (393, 852), lambda size, scale: make_wallpaper(size, scale, chat=False))
    save_scaled("maintabBgImage", (393, 96), lambda size, scale: Image.new("RGB", size, CREAM_2))
    save_scaled("passcodeBgImage", (393, 852), lambda size, scale: make_wallpaper(size, scale, chat=False).filter(ImageFilter.GaussianBlur(1.4 * scale)))


def make_preview() -> None:
    bg = make_wallpaper((1179, 2556), 3, chat=True).convert("RGBA")
    preview = bg.resize((393, 852), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(preview)
    draw.rounded_rectangle((18, 52, 375, 102), radius=12, fill="#FFF8EC")
    draw.text((34, 68), "Kurimanjyu Chic", fill=BROWN_DARK)
    bubbles = [
        ((72, 172), False, "Chic enough?"),
        ((132, 286), True, "Peak kuri mood."),
        ((64, 416), False, "Cream + brown"),
        ((168, 548), True, "Ready for iPhone"),
    ]
    for (x, y), send, text in bubbles:
        bubble = make_bubble((236, 122), 2, send=send, selected=False).resize((212, 110), Image.Resampling.LANCZOS)
        preview.alpha_composite(bubble, (x, y))
        draw.text((x + 46, y + 47), text, fill=BROWN_DARK)
    draw.rounded_rectangle((18, 792, 375, 838), radius=18, fill="#FFF8EC", outline="#E6CFB3")
    draw.text((42, 806), "Message", fill="#9B806B")
    preview.convert("RGB").save(OUTPUTS / "kurimanjyu-chic-preview.png", quality=95)


def make_profile_tab_preview() -> None:
    preview = Image.new("RGBA", (840, 420), CREAM_2)
    draw = ImageDraw.Draw(preview)
    draw.text((24, 20), "Bottom menu - 5 images", fill=BROWN_DARK)
    for idx, kind in enumerate(["friends", "chats", "openchats", "shopping", "more"]):
        x = 50 + idx * 155
        icon = draw_tab_icon(kind, idx == 0, (112, 112), 2)
        preview.alpha_composite(icon, (x, 52))
        draw.text((x + 28, 174), str(idx + 1), fill=BROWN_DARK)
    draw.text((24, 228), "Default profiles - 7 images", fill=BROWN_DARK)
    for idx in range(1, 8):
        profile = Image.open(IMAGES / f"profileImg{idx:02d}@3x.png").convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
        x = 22 + (idx - 1) * 115
        preview.alpha_composite(profile, (x, 264))
        draw.text((x + 42, 375), str(idx), fill=BROWN_DARK)
    preview.convert("RGB").save(OUTPUTS / "kurimanjyu-chic-menu-profiles.png")


def write_css() -> None:
    profile_images = " ".join(f"'profileImg{idx:02d}.png'" for idx in range(1, len(PROFILE_SOURCES) + 1))
    css = f"""/*
 Kurimanjyu Chic - personal iOS KakaoTalk theme
 Generated from the user's four source images for private use.
*/

ManifestStyle {{
    -kakaotalk-theme-name: '{THEME_NAME}';
    -kakaotalk-theme-version: '26.10.0';
    -kakaotalk-theme-url: 'https://www.kakaocorp.com/service/KakaoTalk';
    -kakaotalk-author-name: 'Private Personal Theme';
    -kakaotalk-theme-id: 'com.private.kakaotalk.theme.kurimanjyu.chic';
}}

HeaderStyle-Main {{
    background-color: {CREAM_2};
    -ios-text-color: {BROWN_DARK};
    -ios-tab-text-color: {BROWN_LIGHT};
    -ios-tab-highlighted-text-color: {BROWN_DARK};
}}

MainViewStyle-Primary {{
    background-color: {CREAM_2};
    -ios-background-image: 'mainBgImage.png';
    -ios-text-color: {BROWN_DARK};
    -ios-highlighted-text-color: {BROWN};
    -ios-description-text-color: #8B6B52;
    -ios-description-highlighted-text-color: {BROWN_LIGHT};
    -ios-paragraph-text-color: #9A806A;
    -ios-paragraph-highlighted-text-color: {BROWN_LIGHT};
    -ios-normal-background-color: {CREAM_2};
    -ios-normal-background-alpha: 0.0;
    -ios-selected-background-color: {BROWN};
    -ios-selected-background-alpha: 0.08;
}}

MainViewStyle-Secondary {{
    background-color: {CREAM};
}}

SectionTitleStyle-Main {{
    border-color: {BROWN_LIGHT};
    border-alpha: 0.16;
    -ios-text-color: {BROWN};
    -ios-text-alpha: 0.84;
}}

FeatureStyle-Primary {{
    -ios-text-color: {BROWN};
}}

TabBarStyle-Main {{
    background-color: {CREAM_2};
    -ios-background-image: 'maintabBgImage.png';
    -ios-friends-normal-icon-image: 'maintabIcoFriends.png';
    -ios-friends-selected-icon-image: 'maintabIcoFriendsSelected.png';
    -ios-chats-normal-icon-image: 'maintabIcoChats.png';
    -ios-chats-selected-icon-image: 'maintabIcoChatsSelected.png';
    -ios-browse-normal-icon-image: 'maintabIcoBrowse.png';
    -ios-browse-selected-icon-image: 'maintabIcoBrowseSelected.png';
    -ios-find-normal-icon-image: 'maintabIcoFind.png';
    -ios-find-selected-icon-image: 'maintabIcoFindSelected.png';
    -ios-piccoma-normal-icon-image: 'maintabIcoPiccoma.png';
    -ios-piccoma-selected-icon-image: 'maintabIcoPiccomaSelected.png';
    -ios-game-normal-icon-image: 'maintabIcoGame.png';
    -ios-game-selected-icon-image: 'maintabIcoGameSelected.png';
    -ios-more-normal-icon-image: 'maintabIcoMore.png';
    -ios-more-selected-icon-image: 'maintabIcoMoreSelected.png';
    -ios-openchats-normal-icon-image: 'maintabIcoOpenChats.png';
    -ios-openchats-selected-icon-image: 'maintabIcoOpenChatsSelected.png';
    -ios-shopping-normal-icon-image: 'maintabIcoShopping.png';
    -ios-shopping-selected-icon-image: 'maintabIcoShoppingSelected.png';
}}

DefaultProfileStyle {{
    -ios-profile-images: {profile_images};
}}

MessageCellStyle-Send {{
    -ios-background-image: 'chatroomBubbleSend01.png' 24px 24px;
    -ios-selected-background-image: 'chatroomBubbleSend01Selected.png' 24px 24px;
    -ios-group-background-image: 'chatroomBubbleSend02.png' 24px 24px;
    -ios-group-selected-background-image: 'chatroomBubbleSend02Selected.png' 24px 24px;
    -ios-title-edgeinsets: 10px 12px 7px 16px;
    -ios-group-title-edgeinsets: 10px 12px 7px 16px;
    -ios-text-color: {BROWN_DARK};
    -ios-selected-text-color: {BROWN_DARK};
    -ios-unread-text-color: {BROWN_DARK};
}}

MessageCellStyle-Receive {{
    -ios-background-image: 'chatroomBubbleReceive01.png' 24px 24px;
    -ios-selected-background-image: 'chatroomBubbleReceive01Selected.png' 24px 24px;
    -ios-group-background-image: 'chatroomBubbleReceive02.png' 24px 24px;
    -ios-group-selected-background-image: 'chatroomBubbleReceive02Selected.png' 24px 24px;
    -ios-title-edgeinsets: 10px 16px 7px 12px;
    -ios-group-title-edgeinsets: 10px 16px 7px 12px;
    -ios-text-color: {BROWN_DARK};
    -ios-selected-text-color: {BROWN_DARK};
    -ios-unread-text-color: {BROWN};
}}

BackgroundStyle-ChatRoom {{
    background-color: {CREAM};
    -ios-background-image: 'chatroomBgImage.png';
}}

InputBarStyle-Chat {{
    background-color: {CREAM_2};
    -ios-send-normal-background-color: {BROWN};
    -ios-send-highlighted-background-color: {BROWN_DARK};
    -ios-send-normal-foreground-color: #FFF8EC;
    -ios-send-highlighted-foreground-color: #FFF8EC;
    -ios-button-normal-foreground-color: {BROWN};
    -ios-button-highlighted-foreground-color: {BROWN_DARK};
}}

BackgroundStyle-MessageNotificationBar {{
    background-color: {BROWN};
}}

LabelStyle-MessageNotificationBarName {{
    -ios-text-color: #FFF8EC;
}}

LabelStyle-MessageNotificationBarMessage {{
    -ios-text-color: #F7E4C5;
}}

BackgroundStyle-DirectShareBar {{
    background-color: {CREAM_2};
}}

LabelStyle-DirectShareBarName {{
    -ios-text-color: {BROWN_DARK};
}}

LabelStyle-DirectShareBarMessage {{
    -ios-text-color: {BROWN};
}}

BackgroundStyle-Passcode {{
    background-color: {CREAM};
    -ios-background-image: 'passcodeBgImage.png';
}}

LabelStyle-PasscodeTitle {{
    -ios-text-color: {BROWN_DARK};
}}

PasscodeStyle {{
    -ios-bullet-first-image: 'passcodeImgCode01.png';
    -ios-bullet-second-image: 'passcodeImgCode02.png';
    -ios-bullet-third-image: 'passcodeImgCode03.png';
    -ios-bullet-fourth-image: 'passcodeImgCode04.png';
    -ios-bullet-selected-first-image: 'passcodeImgCode01Selected.png';
    -ios-bullet-selected-second-image: 'passcodeImgCode02Selected.png';
    -ios-bullet-selected-third-image: 'passcodeImgCode03Selected.png';
    -ios-bullet-selected-fourth-image: 'passcodeImgCode04Selected.png';
    -ios-keypad-background-color: #F3D9B8;
    -ios-keypad-text-normal-color: {BROWN_DARK};
    -ios-keypad-number-highlighted-image: 'passcodeKeypadPressed.png';
}}
"""
    (THEME / "KakaoTalkTheme.css").write_text(css, encoding="utf-8")


def build_package() -> dict:
    OUTPUTS.mkdir(exist_ok=True)
    out = OUTPUTS / PACKAGE_NAME
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in [THEME / "KakaoTalkTheme.css", *sorted(IMAGES.glob("*.png"))]:
            zf.write(path, path.relative_to(THEME).as_posix())
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    return {
        "package": str(out),
        "entries": len(names),
        "has_css": "KakaoTalkTheme.css" in names,
        "has_images_dir": any(n.startswith("Images/") for n in names),
        "top_level_folder_wrapped": any(n.startswith("kurimanjyu-ios-theme/") for n in names),
        "sample_entries": names[:10],
    }


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    for file in IMAGES.glob("*.png"):
        file.unlink()

    write_css()
    make_theme_icon()
    make_profiles()
    make_extra_assets()
    make_tab_assets()
    make_passcode_assets()
    for name, send, selected in [
        ("chatroomBubbleSend01", True, False),
        ("chatroomBubbleSend01Selected", True, True),
        ("chatroomBubbleSend02", True, False),
        ("chatroomBubbleSend02Selected", True, True),
        ("chatroomBubbleReceive01", False, False),
        ("chatroomBubbleReceive01Selected", False, True),
        ("chatroomBubbleReceive02", False, False),
        ("chatroomBubbleReceive02Selected", False, True),
    ]:
        save_bubble(name, send=send, selected=selected)
    make_preview()
    make_profile_tab_preview()
    report = build_package()
    (OUTPUTS / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
