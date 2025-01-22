# pyarmor Activation

in powershell in the active venv, to check license status
```
pyarmor -v
```
if needed then register
```
pyarmor reg pyarmor-regfile-7152.zip
```
Generate Self Signed Certificate
```
New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=XXX" -CertStoreLocation MyCert
```
Sign The Exe
```
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe" sign /sm /fd SHA256 /n "XXX" /t http://timestamp.digicert.com /d "Graph Generator Application" GraphGenerator.exe
```
Sign the other tool
```
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe" sign /sm /fd SHA256 /n "XXX" /t http://timestamp.digicert.com /d "Graph Generator Application" pdf-parser.exe
```



