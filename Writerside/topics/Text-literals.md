# Text literals

Text (string) literals can be left unquoted, if they do not contain keywords or other
reserved characters. Moreover, they can be multiline, if each following line starts with
at least `n` spaces, assuming the first line started at n'th symbol in line. E.g.:
```
tech = This is a multiline
       tech specification:
           this is also a part of that text
```
