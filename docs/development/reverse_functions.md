# 重点函数伪 C（main + 各测试项）

## FUN_00105f70 @ 00105f70

```c
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */



undefined8 FUN_00105f70(void)



{

  undefined *puVar1;

  int iVar2;

  undefined8 uVar3;

  undefined8 uVar4;

  undefined8 uVar5;

  undefined8 uVar6;

  code *pcVar7;

  

  DAT_00393a20 = 0xffffffff;

  uVar3 = FUN_00105520(0);

  lv_disp_get_default();

  lv_disp_get_scr_act();

  DAT_00393a30 = lv_obj_create();

  lv_obj_set_size(DAT_00393a30,0x20000064);

  lv_obj_add_style(DAT_00393a30,uVar3,0);

  uVar3 = DAT_00393a30;

  uVar4 = FUN_00105520(0);

  uVar5 = lv_obj_create(uVar3);

  lv_obj_set_size(uVar5,0x20000064,0x46);

  lv_obj_add_style(uVar5,uVar4,0);

  lv_obj_set_style_bg_color(uVar5,0xff586273,0);

  lv_obj_set_scrollbar_mode(uVar5,0);

  uVar3 = lv_obj_create(uVar3);

  lv_obj_set_style_bg_color(uVar3,0xff586273,0);

  lv_obj_set_size(uVar3,300,0x46);

  lv_obj_add_style(uVar3,uVar4,0);

  uVar4 = lv_img_create(uVar3);

  lv_img_set_src(uVar4,PTR_DAT_0013afc0);

  lv_obj_align(uVar4,7,0x19,0);

  uVar6 = lv_label_create(uVar3);

  lv_obj_set_style_text_font(uVar6,PTR_PTR_0013afa0,0);

  lv_obj_set_style_text_color(uVar6,0xffe7e9ec,0);

  lv_label_set_text(uVar6,"rk356x demo");

  lv_obj_align_to(uVar6,uVar4,0x13,10,0);

  uVar3 = lv_label_create(uVar3);

  lv_obj_set_style_text_color(uVar3,0xffe7e9ec,0);

  lv_label_set_text(uVar3,"RTC Test");

  lv_obj_set_style_text_opa(uVar3,0x7f,0);

  puVar1 = PTR_PTR_0013afa8;

  lv_obj_set_style_text_font(uVar3,PTR_PTR_0013afa8,0);

  lv_obj_align_to(uVar3,uVar4,0x15,10,0);

  uVar4 = FUN_00105520(0);

  puRam0000000000393a48 = PTR_s_LED_Test_0013aac8;

  _DAT_00393a40 = PTR_s_RTC_Test_0013aaa8;

  DAT_00393ae0 = "IO Test";

  DAT_00393ae8 = "BT Test";

  puRam0000000000393a58 = PTR_s_Backlight_Test_0013ab08;

  _DAT_00393a50 = PTR_s_Buzzer_Test_0013aae8;

  puRam0000000000393a68 = PTR_s_LightSensor_Test_0013ab48;

  _DAT_00393a60 = PTR_s_KEY_Test_0013ab28;

  puRam0000000000393a78 = PTR_s_ADC_Test_0013ab88;

  _DAT_00393a70 = PTR_s_GSensor_Test_0013ab68;

  puRam0000000000393a88 = PTR_s_TouchScreen_Test_0013abc8;

  _DAT_00393a80 = PTR_s_Audio_Test_0013aba8;

  puRam0000000000393a98 = PTR_s_TF_Card_Test_0013ac08;

  _DAT_00393a90 = PTR_s_U_Disk_Test_0013abe8;

  puRam0000000000393aa8 = PTR_s_UART_Test_0013ac48;

  _DAT_00393aa0 = PTR_s_EEPROM_Test_0013ac28;

  puRam0000000000393ab8 = PTR_s_CAN_Test_0013ac88;

  _DAT_00393ab0 = PTR_s_USB_Serial_Test_0013ac68;

  puRam0000000000393ac8 = PTR_s_Mobile_4G_Test_0013acc8;

  _DAT_00393ac0 = PTR_s_Ethernet_Test_0013aca8;

  puRam0000000000393ad8 = PTR_s_Camera_Test_0013ad08;

  _DAT_00393ad0 = PTR_s_Wifi_Test_0013ace8;

  uVar5 = lv_btnmatrix_create(PTR_s_Wifi_Test_0013ace8,PTR_FUN_0013acf0,PTR_FUN_0013acf8,

                              PTR_FUN_0013ad00,uVar5);

  lv_obj_set_style_pad_left(uVar5,300,0);

  lv_obj_set_size(uVar5,0xec8,0x46);

  lv_btnmatrix_set_map(uVar5,&DAT_00393a40);

  lv_btnmatrix_set_btn_ctrl_all(uVar5,0x150);

  lv_obj_align(uVar5,7,0,0);

  lv_obj_set_style_text_font(uVar5,puVar1,0);

  lv_obj_set_style_text_color(uVar5,0xffe7e9ec,0);

  lv_obj_set_style_text_color(uVar5,0xffe7e9ec,0x50000);

  lv_obj_set_style_text_align(uVar5,2,0);

  lv_btnmatrix_set_one_checked(uVar5,1);

  lv_obj_add_style(uVar5,uVar4,0);

  lv_obj_set_style_pad_column(uVar5,0,0);

  lv_obj_set_style_bg_color(uVar5,0xff586273,0);

  lv_obj_set_style_bg_opa(uVar5,0,0x50000);

  lv_obj_set_style_bg_opa(uVar5,0x33,0x50001);

  lv_obj_set_style_border_width(uVar5,4,0x50001);

  lv_obj_set_style_border_color(uVar5,0xff2196f3,0x50001);

  lv_obj_set_style_border_side(uVar5,1,0x50001);

  lv_obj_set_style_shadow_width(uVar5,0,0x50000);

  lv_obj_set_style_radius(uVar5,0,0x50000);

  DAT_00393af8 = uVar5;

  lv_obj_add_event_cb(uVar5,FUN_00105e78,0x1c,uVar3);

  lv_btnmatrix_set_btn_ctrl(DAT_00393af8,0,0x80);

  uVar3 = DAT_00393a30;

  uVar4 = FUN_00105520(0);

  uVar3 = lv_obj_create(uVar3);

  DAT_00393a28 = uVar3;

  lv_disp_get_default();

  iVar2 = lv_disp_get_ver_res();

  lv_obj_set_size(uVar3,0x20000064,iVar2 + -0x46);

  lv_obj_align(DAT_00393a28,2,0,0x46);

  lv_obj_add_style(DAT_00393a28,uVar4,0);

  lv_obj_set_style_bg_color(DAT_00393a28,0xff444b5a,0);

  if (DAT_00393a20 != 0) {

    if ((DAT_00393a20 != 0xffffffff) &&

       (pcVar7 = *(code **)((long)&PTR_FUN_0013aab8 +

                           (-(ulong)(DAT_00393a20 >> 0x1f) & 0xffffffe000000000 |

                           (ulong)DAT_00393a20 << 5)), pcVar7 != (code *)0x0)) {

      (*pcVar7)();

    }

    FUN_00106a50(DAT_00393a28);

    DAT_00393a20 = 0;

  }

  return 0;

}
```


## FUN_0010731c @ 0010731c  (测试项: ping)

```c
int FUN_0010731c(void)



{

  undefined **ppuVar1;

  char *pcVar2;

  byte bVar3;

  int iVar4;

  long lVar5;

  ulong uVar6;

  

  lVar5 = lv_event_get_target();

  uVar6 = *(ulong *)(lVar5 + 0x20);

  bVar3 = lv_obj_has_state(lVar5,1);

  pcVar2 = "ping 8.8.8.8 -c 1";

  if (bVar3 == 0) {

    pcVar2 = "/dev/input/event0";

  }

  iVar4 = (int)uVar6;

  if (iVar4 == -1) {

    lVar5 = 0;

    do {

      ppuVar1 = &PTR_s__sys_class_gpio_gpio120_value_0013a980 + lVar5;

      lVar5 = lVar5 + 1;

      iVar4 = open(*ppuVar1,1);

      if (iVar4 != -1) {

        write(iVar4,pcVar2 + 0x10,1);

        fsync(iVar4);

        close(iVar4);

      }

    } while (lVar5 != 4);

  }

  else {

    iVar4 = open((&PTR_s__sys_class_gpio_gpio120_value_0013a980)[iVar4],1);

    if (iVar4 != -1) {

      write(iVar4,pcVar2 + 0x10,1);

      fsync(iVar4);

      close(iVar4);

    }

  }

  iVar4 = printf("obj->index: %d, act=%d\n",uVar6 & 0xffffffff,(ulong)bVar3);

  return iVar4;

}
```

## FUN_00107320 @ 00107320  (测试项: ping)

```c
int FUN_00107320(void)



{

  undefined **ppuVar1;

  char *pcVar2;

  byte bVar3;

  int iVar4;

  long lVar5;

  ulong uVar6;

  

  lVar5 = lv_event_get_target();

  uVar6 = *(ulong *)(lVar5 + 0x20);

  bVar3 = lv_obj_has_state(lVar5,1);

  pcVar2 = "ping 8.8.8.8 -c 1";

  if (bVar3 == 0) {

    pcVar2 = "/dev/input/event0";

  }

  iVar4 = (int)uVar6;

  if (iVar4 == -1) {

    lVar5 = 0;

    do {

      ppuVar1 = &PTR_s__sys_class_gpio_gpio120_value_0013a980 + lVar5;

      lVar5 = lVar5 + 1;

      iVar4 = open(*ppuVar1,1);

      if (iVar4 != -1) {

        write(iVar4,pcVar2 + 0x10,1);

        fsync(iVar4);

        close(iVar4);

      }

    } while (lVar5 != 4);

  }

  else {

    iVar4 = open((&PTR_s__sys_class_gpio_gpio120_value_0013a980)[iVar4],1);

    if (iVar4 != -1) {

      write(iVar4,pcVar2 + 0x10,1);

      fsync(iVar4);

      close(iVar4);

    }

  }

  iVar4 = printf("obj->index: %d, act=%d\n",uVar6 & 0xffffffff,(ulong)bVar3);

  return iVar4;

}
```

## FUN_0010baa0 @ 0010baa0  (测试项: ping)

```c
int FUN_0010baa0(void)



{

  int iVar1;

  FILE *__stream;

  char *pcVar2;

  char acStack_108 [264];

  

  sprintf(acStack_108,"ping %s -c 1",&DAT_003941c0);

  __stream = popen(acStack_108,"r");

  iVar1 = 0;

  if (__stream != (FILE *)0x0) {

    while (pcVar2 = fgets(&DAT_00393dc0,0x400,__stream), pcVar2 != (char *)0x0) {

      while ((DAT_00393dc0 != '\0' &&

             (pcVar2 = strstr(&DAT_00393dc0,"bytes from"), pcVar2 != (char *)0x0))) {

        lv_textarea_add_text(DAT_00393db0,&DAT_00393dc0);

        pcVar2 = fgets(&DAT_00393dc0,0x400,__stream);

        if (pcVar2 == (char *)0x0) goto LAB_0010bb44;

      }

    }

LAB_0010bb44:

    iVar1 = pclose(__stream);

  }

  return iVar1;

}
```

## FUN_0010c0e0 @ 0010c0e0  (测试项: ping)

```c
int FUN_0010c0e0(void)



{

  int iVar1;

  FILE *__stream;

  char *pcVar2;

  char local_108 [8];

  char acStack_100 [8];

  char local_f8 [248];

  

  local_108 = (char  [8])s_ping_8_8_8_8__c_1_001276b8._0_8_;

  acStack_100 = (char  [8])s_ping_8_8_8_8__c_1_001276b8._8_8_;

  local_f8._0_2_ = s_ping_8_8_8_8__c_1_001276b8._16_2_;

  __stream = popen(local_108,"r");

  iVar1 = 0;

  if (__stream != (FILE *)0x0) {

    while (pcVar2 = fgets(&DAT_00394220,0x400,__stream), pcVar2 != (char *)0x0) {

      while ((DAT_00394220 != '\0' &&

             (pcVar2 = strstr(&DAT_00394220,"bytes from"), pcVar2 != (char *)0x0))) {

        lv_textarea_add_text(DAT_00394210,&DAT_00394220);

        pcVar2 = fgets(&DAT_00394220,0x400,__stream);

        if (pcVar2 == (char *)0x0) goto LAB_0010c184;

      }

    }

LAB_0010c184:

    iVar1 = pclose(__stream);

  }

  return iVar1;

}
```

## FUN_0010c3a4 @ 0010c3a4  (测试项: SIM Test)

```c
undefined8 FUN_0010c3a4(undefined8 param_1)



{

  int iVar1;

  undefined8 uVar2;

  undefined8 uVar3;

  undefined8 uVar4;

  

  uVar2 = FUN_00105520(0);

  DAT_00394620 = lv_obj_create(param_1);

  lv_obj_set_size(DAT_00394620,0x20000064,0x20000064);

  lv_obj_add_style(DAT_00394620,uVar2,0);

  lv_obj_set_style_bg_color(DAT_00394620,0xff444b5a,0);

  lv_obj_set_style_text_font(DAT_00394620,PTR_PTR_0013afa8,0);

  lv_obj_set_style_text_color(DAT_00394620,0xffe7e9ec,0);

  uVar2 = DAT_00394620;

  uVar3 = lv_obj_create(DAT_00394620);

  lv_obj_set_size(uVar3,800,400);

  lv_obj_set_style_border_color(uVar3,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar3,0xff586273,0);

  lv_obj_align(uVar3,2,0,0x1e);

  lv_obj_set_style_text_color(uVar3,0xffe7e9ec,0);

  DAT_00394210 = lv_textarea_create(uVar3);

  lv_obj_set_size(DAT_00394210,0x20000064,0x20000064);

  lv_obj_set_style_bg_opa(DAT_00394210,0xffffffff,0);

  lv_obj_set_style_bg_color(DAT_00394210,0xffffffff,0);

  lv_obj_clear_flag(DAT_00394210,4);

  lv_obj_align(DAT_00394210,9,0,0);

  uVar4 = lv_btn_create(uVar2);

  lv_obj_set_size(uVar4,0xb4,0x32);

  lv_obj_set_style_shadow_width(uVar4,0,0);

  lv_obj_set_style_radius(uVar4,10,0);

  lv_obj_set_style_border_width(uVar4,2,0);

  lv_obj_set_style_border_color(uVar4,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar4,0xff505060,0);

  lv_obj_set_style_bg_color(uVar4,0xfff44336,0x20);

  lv_obj_align_to(uVar4,uVar3,0xd,0,0x14);

  lv_obj_add_event_cb(uVar4,FUN_0010c008,7,0);

  lv_obj_add_flag(uVar4,1);

  uVar4 = lv_label_create(uVar4);

  lv_label_set_text(uVar4,"Start");

  lv_obj_set_style_text_color(uVar4,0xffe7e9ec,0);

  lv_obj_align(uVar4,9,0,0);

  uVar2 = lv_btn_create(uVar2);

  lv_obj_set_size(uVar2,0xb4,0x32);

  lv_obj_set_style_shadow_width(uVar2,0,0);

  lv_obj_set_style_radius(uVar2,10,0);

  lv_obj_set_style_border_width(uVar2,2,0);

  lv_obj_set_style_border_color(uVar2,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar2,0xff505060,0);

  lv_obj_set_style_bg_color(uVar2,0xfff44336,0x20);

  lv_obj_align_to(uVar2,uVar3,0xe,0,0x14);

  lv_obj_add_event_cb(uVar2,FUN_0010c1a0,7,0);

  uVar2 = lv_label_create(uVar2);

  lv_label_set_text(uVar2,"SIM Test");

  lv_obj_set_style_text_color(uVar2,0xffe7e9ec,0);

  lv_obj_align(uVar2,9,0,0);

  system("ifconfig eth0 down");

  iVar1 = system("ifconfig wlan0 down");

  DAT_00394628 = 0;

  DAT_0039462c = FUN_001052a0(iVar1);

  return 0;

}
```

## FUN_0010c3a8 @ 0010c3a8  (测试项: SIM Test)

```c
undefined8 FUN_0010c3a8(undefined8 param_1)



{

  int iVar1;

  undefined8 uVar2;

  undefined8 uVar3;

  undefined8 uVar4;

  

  uVar2 = FUN_00105520(0);

  DAT_00394620 = lv_obj_create(param_1);

  lv_obj_set_size(DAT_00394620,0x20000064,0x20000064);

  lv_obj_add_style(DAT_00394620,uVar2,0);

  lv_obj_set_style_bg_color(DAT_00394620,0xff444b5a,0);

  lv_obj_set_style_text_font(DAT_00394620,PTR_PTR_0013afa8,0);

  lv_obj_set_style_text_color(DAT_00394620,0xffe7e9ec,0);

  uVar2 = DAT_00394620;

  uVar3 = lv_obj_create(DAT_00394620);

  lv_obj_set_size(uVar3,800,400);

  lv_obj_set_style_border_color(uVar3,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar3,0xff586273,0);

  lv_obj_align(uVar3,2,0,0x1e);

  lv_obj_set_style_text_color(uVar3,0xffe7e9ec,0);

  DAT_00394210 = lv_textarea_create(uVar3);

  lv_obj_set_size(DAT_00394210,0x20000064,0x20000064);

  lv_obj_set_style_bg_opa(DAT_00394210,0xffffffff,0);

  lv_obj_set_style_bg_color(DAT_00394210,0xffffffff,0);

  lv_obj_clear_flag(DAT_00394210,4);

  lv_obj_align(DAT_00394210,9,0,0);

  uVar4 = lv_btn_create(uVar2);

  lv_obj_set_size(uVar4,0xb4,0x32);

  lv_obj_set_style_shadow_width(uVar4,0,0);

  lv_obj_set_style_radius(uVar4,10,0);

  lv_obj_set_style_border_width(uVar4,2,0);

  lv_obj_set_style_border_color(uVar4,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar4,0xff505060,0);

  lv_obj_set_style_bg_color(uVar4,0xfff44336,0x20);

  lv_obj_align_to(uVar4,uVar3,0xd,0,0x14);

  lv_obj_add_event_cb(uVar4,FUN_0010c008,7,0);

  lv_obj_add_flag(uVar4,1);

  uVar4 = lv_label_create(uVar4);

  lv_label_set_text(uVar4,"Start");

  lv_obj_set_style_text_color(uVar4,0xffe7e9ec,0);

  lv_obj_align(uVar4,9,0,0);

  uVar2 = lv_btn_create(uVar2);

  lv_obj_set_size(uVar2,0xb4,0x32);

  lv_obj_set_style_shadow_width(uVar2,0,0);

  lv_obj_set_style_radius(uVar2,10,0);

  lv_obj_set_style_border_width(uVar2,2,0);

  lv_obj_set_style_border_color(uVar2,0xff808a97,0);

  lv_obj_set_style_bg_color(uVar2,0xff505060,0);

  lv_obj_set_style_bg_color(uVar2,0xfff44336,0x20);

  lv_obj_align_to(uVar2,uVar3,0xe,0,0x14);

  lv_obj_add_event_cb(uVar2,FUN_0010c1a0,7,0);

  uVar2 = lv_label_create(uVar2);

  lv_label_set_text(uVar2,"SIM Test");

  lv_obj_set_style_text_color(uVar2,0xffe7e9ec,0);

  lv_obj_align(uVar2,9,0,0);

  system("ifconfig eth0 down");

  iVar1 = system("ifconfig wlan0 down");

  DAT_00394628 = 0;

  DAT_0039462c = FUN_001052a0(iVar1);

  return 0;

}
```

## FUN_0010c770 @ 0010c770  (测试项: ping)

```c
void FUN_0010c770(void)



{

  int iVar1;

  uint uVar2;

  ulong uVar3;

  FILE *__stream;

  char *pcVar4;

  ulong uVar5;

  

  uVar5 = (ulong)DAT_0039462c;

  uVar3 = FUN_001052a0();

  if ((long)(uVar5 - (uVar3 & 0xffffffff)) < 0) {

    if (DAT_00394628 == 0) {

      __stream = popen("ip route show","r");

      uVar3 = 0;

      if (__stream != (FILE *)0x0) {

        while (pcVar4 = fgets(&DAT_00394220,0x400,__stream), pcVar4 != (char *)0x0) {

          pcVar4 = strstr(&DAT_00394220,"proto kernel scope link src");

          if (pcVar4 != (char *)0x0) {

            __isoc99_sscanf(&DAT_00394220,"%31s dev %*s proto kernel scope link src %31s",

                            &DAT_00394650,&DAT_00394630);

            sprintf(&DAT_00394220,"\nIP: %s\nGATE: %s\n\n",&DAT_00394630,&DAT_00394650);

            printf(&DAT_00394220);

            lv_textarea_add_text(DAT_00394210,&DAT_00394220);

            lv_textarea_add_text(DAT_00394210,"Test ping \'8.8.8.8\'\n");

            DAT_00394628 = 1;

          }

        }

        uVar2 = pclose(__stream);

        uVar3 = (ulong)uVar2;

      }

    }

    else {

      uVar3 = FUN_0010c0e0();

    }

    iVar1 = FUN_001052a0(uVar3);

    DAT_0039462c = iVar1 + 2000;

    return;

  }

  return;

}
```

## FUN_0010cccc @ 0010cccc  (测试项: ping)

```c
int FUN_0010cccc(void)



{

  int iVar1;

  FILE *__stream;

  char *pcVar2;

  char acStack_108 [264];

  

  sprintf(acStack_108,"ping %s -c 1",&DAT_00394c00);

  __stream = popen(acStack_108,"r");

  iVar1 = 0;

  if (__stream != (FILE *)0x0) {

    while (pcVar2 = fgets(&DAT_00394680,0x400,__stream), pcVar2 != (char *)0x0) {

      while ((DAT_00394680 != '\0' &&

             (pcVar2 = strstr(&DAT_00394680,"bytes from"), pcVar2 != (char *)0x0))) {

        lv_textarea_add_text(DAT_00394c20,&DAT_00394680);

        pcVar2 = fgets(&DAT_00394680,0x400,__stream);

        if (pcVar2 == (char *)0x0) goto LAB_0010cd74;

      }

    }

LAB_0010cd74:

    iVar1 = pclose(__stream);

  }

  return iVar1;

}
```

## FUN_0010ccd0 @ 0010ccd0  (测试项: ping)

```c
int FUN_0010ccd0(void)



{

  int iVar1;

  FILE *__stream;

  char *pcVar2;

  char acStack_108 [264];

  

  sprintf(acStack_108,"ping %s -c 1",&DAT_00394c00);

  __stream = popen(acStack_108,"r");

  iVar1 = 0;

  if (__stream != (FILE *)0x0) {

    while (pcVar2 = fgets(&DAT_00394680,0x400,__stream), pcVar2 != (char *)0x0) {

      while ((DAT_00394680 != '\0' &&

             (pcVar2 = strstr(&DAT_00394680,"bytes from"), pcVar2 != (char *)0x0))) {

        lv_textarea_add_text(DAT_00394c20,&DAT_00394680);

        pcVar2 = fgets(&DAT_00394680,0x400,__stream);

        if (pcVar2 == (char *)0x0) goto LAB_0010cd74;

      }

    }

LAB_0010cd74:

    iVar1 = pclose(__stream);

  }

  return iVar1;

}
```