# pyfilename

**Make names comply various filename constraints of Windows.**

**윈도우의 복잡한 파일명 제한들을 만족시키는 안전한 이름을 만듭니다.**

윈도우는 POSIX 운영체제들과 달리 파일 이름에 매우 엄격한 제약이 있습니다.
pyfilename을 사용하면 제한된 문자를 제거하거나 전각 문자로 변환하여 기존 문자의 의미를 손상시키지 않고
윈도우에서 유효한 파일명을 생성해낼 수 있습니다.

> [!NOTE]
> 파일명과 폴더명은 같은 것이니 폴더명에도 안심하고 사용하세요.

## Installation

pip을 통해 이 프로젝트를 설치할 수 있습니다.

```console
pip install -U pyfilename
```

## Functions that pyfilename have

아래에서는 pyfilename에 있는 함수들을 간단히 설명합니다.

각 함수의 메소드나 자세한 기능에 대한 설명은 각 함수의 docstring을 참고하세요.

* `convert`: 안전한 파일명을 생성합니다.
* `revert`: 안전해진 파일명을 다시 원래 문자열로 되돌립니다.
* `is_safe`: 파일명이 안전하고 온전한지 확인합니다.
* `is_creatable`: 파일명이 '생성 가능한지' 확인합니다. 생성 시 파일명이 변경되는 것을 원하지 않으면 `is_safe`를 사용하세요.

## 예시

```python
>>> import pyfilename as pf
>>>
>>> pf.is_safe('hello_world?.txt')  # Character '?' is invalid to use in file name
False
>>> safe_name = pf.convert('hello_world?.txt')  # Convert to safe name
>>> safe_name
'hello_world？.txt'
>>> pf.is_safe(safe_name)  # Now it's True.
True
```

## 주의사항

* 백슬래시(\\)의 대안 문자(⧵, REVERSE SOLIDUS OPERATOR)는 윈도우 기본 zip 파일 제작기에서 입력되지 못합니다. [반디집](https://kr.bandisoft.com/bandizip/)과 같은 다른 zip파일 생성 툴을 이용하거나 fullwidth 모드 대신 다른 모드를 사용하세요.

## 비슷한 프로젝트

[pathvalidate](https://github.com/thombashi/pathvalidate)는 파일 경로 문자열을 검사합니다. 하지만 대체 문자를 사용하는 등의 기능은 없습니다.

## 파일명 길이

pyfilename은 전체 경로가 아닌 파일명을 확인하는 라이브러리이고, 윈도우에서는 최대 경로 길이를 조절할 수 있기 때문에 일반화가 어려워 모든 함수들에서 파일명 길이는 확인되지 않습니다.

## Relese Note

* 0.5.0 (2024/04/??): 현대화 및 전체적인 개선 및 오류 수정
* 0.2.0 (2023/09/10): 전체적인 구현 변경
* 0.1.0: 첫 릴리즈
