# Kurimanjyu Chic iOS KakaoTalk Theme

개인 사용을 전제로 만든 iPhone 16 Pro용 카카오톡 iOS 사용자 테마입니다. 업로드된 쿠리만쥬 이미지 4장을 원본으로 보존하고, 배경/말풍선/테마 아이콘/기본 프로필/탭 아이콘을 재생성합니다.

## 확인한 공식 규격

- 카카오 공식 iOS 사용자 테마 가이드는 `.ktheme`가 루트의 `KakaoTalkTheme.css`와 `Images/` 폴더로 구성된 ZIP 패키지라고 설명합니다.
- 이미지와 색상은 변경 가능하지만 레이아웃은 변경할 수 없습니다.
- 이미지 리소스는 CSS에서 기본 파일명으로 참조하고, 실제 에셋은 `@2x`, `@3x` 배율 파일을 함께 두는 방식이 권장됩니다.
- 채팅방 배경은 `BackgroundStyle-ChatRoom`, 말풍선은 `MessageCellStyle-Send`와 `MessageCellStyle-Receive`, 테마 목록 아이콘은 `Images/commonIcoTheme.png`를 사용합니다.
- 설치는 완성된 ZIP의 확장자를 `.ktheme`로 바꾼 뒤 Safari 링크 또는 카카오톡 전송으로 여는 흐름입니다.

## 말풍선 스타일

보낸 메시지와 받은 메시지 모두 숙취쿠리 얼굴에서 추출한 회녹색(#AEBCA0) 말풍선과 어두운 브라운(#3E2A1F) 글씨를 사용합니다. 선택 시 말풍선은 #98A88A입니다. 장식, 테두리, 그림자를 제거하고 기본 스타일의 둥근 말풍선으로 제작했습니다. 첫 메시지에는 작은 기본형 꼬리가 있으며 연속 메시지에는 없습니다. 카카오톡 자체 기본 리소스를 그대로 사용하는 설정이 아니라 테마 이미지로 재현한 형태이므로 실제 앱과 픽셀 단위로 동일하다고 보장하지 않습니다.

## 하단 메뉴와 기본 프로필

하단 메뉴 5종은 첨부 순서의 캬.jpg, 캬3.jpg, 쿠리쿠리.webp, 쿠쿠리.webp, 캬2.png를 사용합니다. 친구/채팅/오픈채팅(구 browse)/쇼핑/더보기 순서로 지정하며 실제 탭 이름과 지원 여부는 앱 버전에 따릅니다. 선택 시 테두리와 표시선으로 구분됩니다.

기본 프로필은 위 5장과 쿠리리.webp, 숙취쿠리.webp를 합쳐 7종을 등록했습니다. 이미 프로필 사진이 있는 친구의 사진은 바뀌지 않습니다. 기본 프로필 목록의 선택과 배정은 카카오톡 내부 동작에 따릅니다. 공식 가이드 예시는 3종이며 7종 지원이나 매번 무작위 재배정은 명시하지 않으므로 iPhone에서 실제로 7종이 사용되는지 확인해야 합니다.

## 폰트 한계

어비 찌바체 같은 커스텀 폰트를 카카오톡 iOS 사용자 테마 안에서 직접 지정하는 CSS 속성은 공식 가이드 범위에 없습니다. 이 테마는 폰트 파일을 억지로 넣지 않고, 카카오톡/iOS가 렌더링하는 기본 글꼴을 사용합니다. 글자 이미지가 필요한 로고나 미리보기에는 별도 이미지로 표현할 수 있지만 채팅 텍스트 자체는 바뀌지 않습니다.

## 구조

```text
work/
  source-images/              원본 첨부 이미지 사본
  build_theme.py              이미지 생성 및 .ktheme 패키징
  validate_theme.py           .ktheme 구조 검사
  kurimanjyu-ios-theme/
    KakaoTalkTheme.css
    Images/
outputs/
  kurimanjyu-chic.ktheme
  kurimanjyu-chic-preview.png
  build-report.json
```

## 다시 빌드하기

```powershell
python work\build_theme.py
python work\validate_theme.py outputs\kurimanjyu-chic.ktheme
```

## iPhone 설치 방법

1. `outputs/kurimanjyu-chic.ktheme` 파일을 iPhone으로 보냅니다. 가장 쉬운 방법은 카카오톡 나에게 보내기입니다.
2. iPhone 카카오톡에서 받은 `.ktheme` 파일을 엽니다.
3. 테마 설치 안내가 뜨면 테마 목록으로 이동해 `Kurimanjyu Chic`을 적용합니다.
4. 적용 후 카카오톡을 재시작하면 더 안정적으로 반영됩니다.

## 실기기에서 꼭 확인할 점

- iPhone 16 Pro의 실제 카카오톡 화면에서 채팅방 배경 크롭 위치가 마음에 드는지 확인해야 합니다.
- 카카오톡 업데이트에 따라 일부 CSS 키가 무시되거나 다른 화면에 함께 적용될 수 있습니다.
- 말풍선은 9-slice 방식으로 늘어나므로 아주 긴 메시지에서 꼬리와 모서리 왜곡이 없는지 확인하면 좋습니다.
- 업로드된 캐릭터 이미지는 권리 상태를 이 환경에서 독립적으로 검증할 수 없으므로 개인 사용 범위 안에서만 사용하세요.
- 사용자가 이미지를 직접 준비해야 합니다.