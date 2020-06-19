#include "mem.h"
#include "c_types.h"
#include "user_interface.h"
#include "ets_sys.h"
#include <uart.h>
#include "osapi.h"
#include "espconn.h"
#include "esp_rawsend.h"
#include "esp82xxutil.h"

#define procTaskPrio 0
#define procTaskQueueLen 1

char generic_print_buffer[384];

static struct espconn *pUdpServer;

static volatile os_timer_t some_timer;

static inline uint32_t asm_ccount(void) {
    int32_t r;
    asm volatile ("rsr %0, ccount" : "=r"(r));
    return (uint32_t)r;
}

// Tasks that happen all the time.
os_event_t procTaskQueue[procTaskQueueLen];
static void ICACHE_FLASH_ATTR
procTask(os_event_t *events) {
    system_os_post(procTaskPrio, 0, 0);

    if (events->sig == 0 && events->par == 0)
    {
        //Idle Event.
    }
    //	printf( "+" );
    //	ets_delay_us( 20000 );
    //	printf( "-" );
}

uint8_t mypacket[30 + 256] = {
    //256 = max size of additional payload
    0x08, //Frame type, 0x80 = beacon, Tried data, but seems to have been filtered on RX side by other ESP
    0x00, 0x00, 0x00,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0x00, 0x00,             //Sequence number, cleared by espressif
    0x82, 0x66,             //"Mysterious OLPC stuff"
    0x82, 0x66, 0x00, 0x00, //????
};

volatile uint32_t debugccount;
volatile uint32_t sent_packet_cnt;
volatile uint32_t received_packet_cnt;
volatile uint32_t debugcontrol;

volatile uint32_t packet_tx_time;
volatile uint32_t packet_tx_matchmask = 0x10000;

volatile uint32_t packet_rx_time;
volatile uint32_t packet_rx_matchmask = 0x10000;

static uint8_t packet_received;
static uint8_t packet_sent;

uint8_t tx_packet_status;

void udpserver_recv(void *arg, char *pusrdata, unsigned short len) {
    struct espconn *pespconn = (struct espconn *)arg;
    // Not used.
}

#define MAX_BUFFERS 10
#define BUFFERSIZE 40
uint8_t buffers[MAX_BUFFERS][BUFFERSIZE];
uint8_t bufferinuse[MAX_BUFFERS];

void __attribute__((noinline)) rx_func(struct RxPacket *r, void **v)
{
    packet_rx_time = asm_ccount();
    if (r->data[24] != 0x82 || r->data[25] != 0x66 || r->data[26] != 0x82 || r->data[27] != 0x66)
    {
        return;
    }
    int b = 0;
    for (b = 0; b < MAX_BUFFERS; b++)
    {
        if (bufferinuse[b] == 0)
            break;
    }
    if (b == MAX_BUFFERS)
        return;

    uint8_t *buffout = buffers[b];
    ets_memcpy(buffout, r, 6);                         //Header
    ets_memcpy(buffout + 6, ((uint8_t *)r) + 22, 6);   //MAC From
    ets_memcpy(buffout + 12, mypacket + 10, 6);        //My MAC
    ets_memcpy(buffout + 18, ((uint8_t *)r) + 42, 20); //ESPEED?
    //Two bytes at end of buffer are reserved.

    received_packet_cnt = received_packet_cnt + 1;
    bufferinuse[b] = 1;
    packet_received = 1;

    //	buffout[36] = debugccount>>24;
    //	buffout[37] = debugccount>>16;
    //	buffout[38] = debugccount>>8;
    //	buffout[39] = debugccount>>0; No longer needed, put in place by interrupt.

    //	espconn_sent(pUdpServer, buffout, 40 ); //+8 = include header

    //Tricky: Can't call espconn_sent from inside here.
}


static void ClearOutBuffers() {
    int b;
    for (b = 0; b < MAX_BUFFERS; b++) {
        bufferinuse[b] = 0;
    }
}

static void SendBufferToServer(uint32_t rtof, uint32_t packet_cnt){

    uint8_t buffout[BUFFERSIZE];
    ets_memcpy(buffout, "\x00\x00\x00\x00\x00\x00", 6); //Header
    ets_memcpy(buffout + 6, mypacket + 10, 6);          //MAC From (us)
    ets_memcpy(buffout + 12, mypacket + 10, 6);         //My MAC (us)
    ets_memcpy(buffout + 18, "ESPPIT", 6);              //ESPTXX

    buffout[24] = packet_cnt >> 24;
    buffout[25] = packet_cnt >> 16;
    buffout[26] = packet_cnt >> 8;
    buffout[27] = packet_cnt >> 0;

    buffout[28] = rtof >> 0;
    buffout[29] = rtof >> 8;
    buffout[30] = rtof >> 16;
    buffout[31] = rtof >> 24;
    espconn_sent(pUdpServer, buffout, BUFFERSIZE);
}

int txpakid;

void set_tx_status(uint8 status) {
    if(status == 0){
        packet_sent = 1;
    } else {
        packet_sent = 0;
    }
}

//Timer event.
extern uint8_t printed_ip;
extern uint8_t *wDevCtrl;

void PreEmpt_NMI_Vector();
static void ICACHE_FLASH_ATTR myTimer(void *arg) {
    static int thistik;
    static int waittik;
    
    //waittik = rand() % 10 + 40;
    waittik = 100;
    thistik++;

    CSTick(0);
    // printf("!!%d\n", received_packet_cnt);

    //	wifi_set_user_fixed_rate( 3, 0x0b );  //0xb = 6Mbit G
    //	wifi_set_user_fixed_rate( 3, 0x0c );  //0xc = 54Mbit G
    //	wifi_set_user_fixed_rate( 3, 0x07 );  //0x7 = 11Mbit ... B?

    //0x02 = 5.5Mbit/s (B)
    //0x01 = 2Mbit/s (B)
    //0x00 = 1Mbit/s (B)
    //0x10 = 6.5MBit
    //0x11 = 13MBit
    //0x1f = 72.2Mbit/s
    //	wifi_set_phy_mode(PHY_MODE_11N);

    //54 mbit
    //	wifi_set_phy_mode(PHY_MODE_11G); //??? Maybe - I haven't been doing this...
    //	wifi_set_user_fixed_rate( 3, 0x0c );

    wifi_set_phy_mode(PHY_MODE_11N); //??? Maybe - I haven't been doing this...
    wifi_set_user_fixed_rate(3, 0x1f);

    //	wifi_set_user_limit_rate_mask( 3 );
    //	wifi_set_user_rate_limit( FIXED_RATE_MASK_ALL, 0, 1, 1 );
    if (packet_sent && packet_received) {
        printf("----------------------------------\n");
        printf("RX cc: %u TX cc: %u Diff: %u\n", packet_rx_time, packet_tx_time, (packet_rx_time - packet_tx_time));
        printf("Packet NR. %u\n", received_packet_cnt);
        printf("----------------------------------\n");
        SendBufferToServer((packet_rx_time - packet_tx_time), received_packet_cnt);
        ClearOutBuffers();
        packet_sent = 0;
        packet_received = 0;

        thistik = 0;
    }
    if (thistik >= waittik) {
        thistik = 0;
        packet_sent = 0;
        packet_received = 0;
        CSTick(1);
    }
    if (thistik == 15)
    {
        int i;
        static int did_init = 0;

        if (!did_init)
        {
            //For sending raw packets.
            //SetupRawsend();
            wifi_set_raw_recv_cb(rx_func);

            // wifi_register_send_pkt_freedom_cb(sent_freedom_cb);
            wifi_register_send_pkt_freedom_cb(set_tx_status);
            did_init = 1;

            //Setup our send packet with our MAC address.
            wifi_get_macaddr(STATION_IF, mypacket + 10);
            debugccount = 0;

            //printf( "!!!\n" );
        }

        //printf( "%d\n", debugccount );
        //uart0_sendStr("k");
        ets_strcpy(mypacket + 30, "ESPEED");
        txpakid++;
        mypacket[36] = txpakid>>24;
        mypacket[37] = txpakid>>16;
        mypacket[38] = txpakid>>8;
        mypacket[39] = txpakid>>0;
        mypacket[40] = 0;
        mypacket[41] = 0;
        mypacket[42] = 0;
        mypacket[43] = 0;

        packet_tx_time = 0;
        wifi_send_pkt_freedom(mypacket, 30 + 16, true);
        //Looks like we can actually set the speed --> wifi_set_user_fixed_rate( 3, 12 );
    }
}

void ICACHE_FLASH_ATTR charrx(uint8_t c)
{ /*Called from UART.*/
}

void user_init(void)
{
    uart_init(BIT_RATE_115200, BIT_RATE_115200);
    uart_init(BIT_RATE_115200, BIT_RATE_115200);

    debugcontrol = 0xffffffff;

    system_update_cpu_freq(160);

    uart0_sendStr("testing...\r\n\033ctesting"); //Clear screen
    uart0_sendStr("\r\nesp82XX Web-GUI\r\n" VERSSTR "\b");

    printf("\nHello from pitcher!\n");

    packet_sent = 0;
    packet_received = 0;
    packet_rx_time = 0;
    packet_tx_time = 0;
    tx_packet_status = 0;
    received_packet_cnt = 0;

    struct rst_info *r = system_get_rst_info();
    printf("Reason: %p\n", r->reason);
    printf("Exec  : %p\n", r->exccause);
    printf("epc1  : %p\n", r->epc1);
    printf("epc2  : %p\n", r->epc2);
    printf("epc3  : %p\n", r->epc3);
    printf("excvaddr:%p\n", r->excvaddr);
    printf("depc: %p\n", r->depc);

    CSSettingsLoad(0);
    CSPreInit();

    CSInit();

    //Set GPIO16 for INput
    WRITE_PERI_REG(PAD_XPD_DCDC_CONF,
                   (READ_PERI_REG(PAD_XPD_DCDC_CONF) & 0xffffffbc) | (uint32)0x1); // mux configuration for XPD_DCDC and rtc_gpio0 connection

    WRITE_PERI_REG(RTC_GPIO_CONF,
                   (READ_PERI_REG(RTC_GPIO_CONF) & (uint32)0xfffffffe) | (uint32)0x0); //mux configuration for out enable

    WRITE_PERI_REG(RTC_GPIO_ENABLE,
                   READ_PERI_REG(RTC_GPIO_ENABLE) & (uint32)0xfffffffe); //out disable

    SetServiceName("ws2812");
    AddMDNSName("esp82xx");
    AddMDNSName("rawpack");
    AddMDNSService("_http._tcp", "An ESP8266 Webserver", WEB_PORT);
    AddMDNSService("_esp82xx._udp", "ESP8266 Backend", BACKEND_PORT);

    pUdpServer = (struct espconn *)os_zalloc(sizeof(struct espconn));
    ets_memset(pUdpServer, 0, sizeof(struct espconn));
    espconn_create(pUdpServer);
    pUdpServer->type = ESPCONN_UDP;
    pUdpServer->proto.udp = (esp_udp *)os_zalloc(sizeof(esp_udp));
    pUdpServer->proto.udp->local_port = 9999;
    pUdpServer->proto.udp->remote_port = 9999;
    pUdpServer->proto.udp->remote_ip[0] = 192;
    pUdpServer->proto.udp->remote_ip[1] = 168;
    pUdpServer->proto.udp->remote_ip[2] = 4;
    pUdpServer->proto.udp->remote_ip[3] = 3;
    espconn_regist_recvcb(pUdpServer, udpserver_recv);
    if (espconn_create(pUdpServer))
        while (1)
            uart0_sendStr("\r\nFAULT\r\n");

    //XXX TODO figure out how to safely re-allow this.

    //Add a process
    system_os_task(procTask, procTaskPrio, procTaskQueue, procTaskQueueLen);

    uart0_sendStr("\r\nCustom Server\r\n");

    //Timer example
    os_timer_disarm(&some_timer);
    os_timer_setfn(&some_timer, (os_timer_func_t *)myTimer, NULL);
    os_timer_arm(&some_timer, 1, 1); //The underlying API expects it's slow ticks to average out to 50ms.

    //system_os_post(procTaskPrio, 0, 0 );

    PIN_DIR_OUTPUT = _BV(2);
    PIN_OUT_SET = _BV(2);
    PIN_OUT_CLEAR = _BV(2);
}

//There is no code in this project that will cause reboots if interrupts are disabled.
void EnterCritical() {}
void ExitCritical() {}

uint32 ICACHE_FLASH_ATTR
user_rf_cal_sector_set(void)
{
    enum flash_size_map size_map = system_get_flash_size_map();
    uint32 rf_cal_sec = 0;

    switch (size_map)
    {
    case FLASH_SIZE_4M_MAP_256_256:
        rf_cal_sec = 128 - 8;
        break;

    case FLASH_SIZE_8M_MAP_512_512:
        rf_cal_sec = 256 - 5;
        break;

    case FLASH_SIZE_16M_MAP_512_512:
    case FLASH_SIZE_16M_MAP_1024_1024:
        rf_cal_sec = 512 - 5;
        break;

    case FLASH_SIZE_32M_MAP_512_512:
    case FLASH_SIZE_32M_MAP_1024_1024:
        rf_cal_sec = 1024 - 5;
        break;

    default:
        rf_cal_sec = 0;
        break;
    }

    return rf_cal_sec;
}
