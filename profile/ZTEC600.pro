interface gpon_olt-@PONID
  onu @ONUINDEX type XGPON1E8C loid @LOID
$
interface gpon_onu-@PONID:@ONUINDEX
  name @NAME
  vport-mode manual
  tcont 1 name Tl1DefaultCreate  profile XGPON1E8C
  sn-bind disable
  gemport 1 name Tl1OpVlan46  tcont 1
  gemport 2 name Tl1OpVlan41  tcont 1
  gemport 3 name Tl1OpVlan45  tcont 1
  encrypt 1 enable downstream
  encrypt 2 enable downstream
  encrypt 3 enable downstream
  vport 1 name singleVPort map-type vlan
  vport-map 1 1 vlan 46
  vport-map 1 2 vlan 41
  vport-map 1 3 vlan 45
$
 interface vport-@PONID.@ONUINDEX:1
  service-port 1 user-vlan 46 vlan 46 svlan @SVLAN
  service-port 2 user-vlan 41 vlan @CVLAN svlan @SVLAN
  service-port 3 user-vlan 45 vlan 45 svlan @SVLAN
  service-port 1 description Tl1OpVlan46
  service-port 2 description Tl1OpVlan41
  service-port 3 description Tl1OpVlan45
$
pon-onu-mng gpon_onu-@PONID:@ONUINDEX
  vlan port veip_1 mode trunk
  vlan port veip_1 vlan 41,45-46,50
  mvlan 50
  service Tl1OpVlan46 gemport 1 vlan 46
  service Tl1OpVlan41 gemport 2 vlan 41
  service Tl1OpVlan45 gemport 3 vlan 45
$
igmp mvlan 50 
 receive-port vport-@PONID.@ONUINDEX:1
$
