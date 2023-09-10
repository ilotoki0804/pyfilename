# pyfilename

안전한 파일 이름을 제공하는 라이브러리입니다.

# 시작하기

1. 파이썬을 설치합니다.
2. cmd 창을 열어 pip 명령어를 실행합니다.
   ```
   pip install -U pyfilename
   ```

# 파일 이름 변환하기

다음과 같은 함수를 통해 파일 이름을 변환할 수 있습니다.

translate_to_safe_name: 파일명으로 사용하기에 안전한 string으로 변환합니다.
translate_to_safe_path_name: 파일 경로로 사용하기에 안전한 string으로 변환합니다.
safe_name_to_original_name: 파일명으로 사용하기에 안전한 string으로 변환한 값을 다시 일반적인 값으로 변경할 때 쓰입니다.
is_vaild_file_name: 파일명으로 쓸 수 있는지 확인합니다. 파일명으로 사용이 부적합하면 False를 반환합니다.

```python
>>> import pyfilename as pf
>>>
>>> pf.is_vaild_file_name('hello_world?.txt')  # Character '?' is invalid to use in file name
False
>>> (safe_name := pf.translate_to_safe_name('hello_world?.txt'))  # Convert to safe name
'hello_world？.txt'
>>> pf.is_vaild_file_name(safe_name)  # Now it's True.
True
```

# Relese Note

0.2.0 (Sep 10, 2023): 전체적인 구현 변경
0.1.0: 첫 릴리즈