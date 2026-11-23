$ErrorActionPreference = 'Stop'
try {
  $dn = 'CN=TBFCWEBSERVER,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=tbfc,DC=loc'
  $entry = [ADSI]("LDAP://$dn")
  $entry.psbase.Options.SecurityMasks = [DirectoryServices.SecurityMasks]::Dacl
  $security = $entry.psbase.ObjectSecurity
  [IO.File]::WriteAllBytes('C:\ProgramData\hopper-template-acl-original.bin', $security.GetSecurityDescriptorBinaryForm())
  $principal = [Security.Principal.NTAccount]'TBFC\TBFC-SQLSERVER1$'
  $enrollGuid = [Guid]'0e10c968-78fb-11d2-90d4-00c04f79dc55'
  $rule = New-Object DirectoryServices.ActiveDirectoryAccessRule($principal, [DirectoryServices.ActiveDirectoryRights]::ExtendedRight, [Security.AccessControl.AccessControlType]::Allow, $enrollGuid, [DirectoryServices.ActiveDirectorySecurityInheritance]::None)
  $security.AddAccessRule($rule)
  $entry.psbase.ObjectSecurity = $security
  $entry.psbase.CommitChanges()
  [IO.File]::WriteAllText('C:\ProgramData\hopper-template-acl-result.txt', 'Enrollment access added to TBFCWEBSERVER for TBFC-SQLSERVER1$')
} catch {
  [IO.File]::WriteAllText('C:\ProgramData\hopper-template-acl-result.txt', $_.ToString() + "`n" + $_.ScriptStackTrace)
  throw
}
