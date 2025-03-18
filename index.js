"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
require("dotenv").config();
const discord_js_1 = require("discord.js");
const instagram_private_api_1 = require("instagram-private-api");
const child_process_1 = require("child_process");
const fs_1 = __importDefault(require("fs"));
const node_cron_1 = __importDefault(require("node-cron"));
const dokdo_1 = require("dokdo");
const client = new discord_js_1.Client({ intents: [discord_js_1.GatewayIntentBits.Guilds, discord_js_1.GatewayIntentBits.GuildMessages, discord_js_1.GatewayIntentBits.MessageContent] });
const instagramid = process.env.InstagramID;
const instagramPassword = process.env.InstagramPassword;
const webhook = process.env.discordwebhook;
const avatarurl = process.env.avatarurl;
const SCHOOLNAME = process.env.SCHOOLNAME;
const botversion = process.env.botversion;
const webhookClient = new discord_js_1.WebhookClient({ url: webhook });
let cronJob = null;
let mealNotificationEnabled = true; // 급식 알림 활성화 여부를 저장하는 변수
let enabledDays = new Set([1, 2, 3, 4, 5]); // 급식 알림을 받을 요일 (0: 일요일, 6: 토요일), 기본적으로 월~금 활성화
const FLAG_FILE = "./flag.json";
const postToInstagram = () => __awaiter(void 0, void 0, void 0, function* () {
    if (!mealNotificationEnabled) {
        console.log("🚫 급식 알림이 비활성화되어 있습니다. 게시물을 전송하지 않습니다.");
        if (client.user) {
            client.user.setActivity("🚫 급식 알림이 비활성화되어 있습니다.", { type: discord_js_1.ActivityType.Watching });
        }
        return;
    }
    const date = new Date();
    if (!enabledDays.has(date.getDay())) {
        console.log("🚫 오늘은 설정된 급식 알림 요일이 아닙니다.");
        if (client.user) {
            client.user.setActivity("🚫 오늘은 설정된 급식 알림 요일이 아닙니다.", { type: discord_js_1.ActivityType.Watching });
        }
        return;
    }
    function dayToKorean(day) {
        const daysOfWeek = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
        return daysOfWeek[day];
    }
    if (getFlag()) {
        console.log("오늘 이미 게시물을 전송했습니다.");
        return;
    }
    console.log("🐍 Python 실행 요청됨");
    (0, child_process_1.exec)(".venv/bin/python3 ./scripts/image_maker.py", (err, stdout, stderr) => __awaiter(void 0, void 0, void 0, function* () {
        console.log("🐍 Python 실행 됨");
        if (err) {
            console.error(err);
            webhookClient.send({
                content: `🛑 Python 오류 발생\n${err}`,
                username: `${SCHOOLNAME} 급식로그`,
                avatarURL: avatarurl,
            });
            return;
        }
        console.log(stdout);
        console.log(stderr);
        const instagram = new instagram_private_api_1.IgApiClient();
        instagram.state.generateDevice(instagramid);
        try {
            yield instagram.account.login(instagramid, instagramPassword);
            console.log("✅ 인스타그램 로그인 성공");
            let items = [];
            const morningData = JSON.parse(fs_1.default.readFileSync("./json/morning.json", "utf8"));
            if (morningData.meals !== null) {
                const food = fs_1.default.readFileSync("./build/morning.jpg");
                items.push({ file: food });
            }
            const lunchData = JSON.parse(fs_1.default.readFileSync("./json/lunch.json", "utf8"));
            if (lunchData.meals !== null) {
                const food2 = fs_1.default.readFileSync("./build/lunch.jpg");
                items.push({ file: food2 });
            }
            const dinnerData = JSON.parse(fs_1.default.readFileSync("./json/dinner.json", "utf8"));
            if (dinnerData.meals !== null) {
                const food3 = fs_1.default.readFileSync("./build/dinner.jpg");
                items.push({ file: food3 });
            }
            console.log("📷 인스타그램에 게시물 올리는 중");
            const todayDate = `${date.getFullYear()}년 ${String(date.getMonth() + 1).padStart(2, "0")}월 ${String(date.getDate()).padStart(2, "0")}일 ${dayToKorean(date.getDay())}`;
            if (items.length === 0) {
                console.log("❌ 오늘은 게시할 급식 정보가 없습니다.");
                webhookClient.send({
                    content: `❌ 오늘은 게시할 급식 정보가 없습니다.`,
                    username: `${SCHOOLNAME} 급식로그`,
                    avatarURL: avatarurl,
                });
            }
            else if (items.length === 1) {
                yield instagram.publish.photo({
                    file: items[0].file,
                    caption: `${todayDate} ${SCHOOLNAME} 급식입니다.\n\n#급식 #급식봇 #${SCHOOLNAME} #${String(date.getDate()).padStart(2, "0")}일`,
                });
                console.log("✅ 인스타그램에 사진이 성공적으로 업로드 되었습니다!");
                webhookClient.send({
                    content: `인스타그램에 급식 사진이 업로드되었습니다! **(${todayDate})**`,
                    username: `${SCHOOLNAME} 급식로그`,
                    avatarURL: avatarurl,
                    files: items.map(item => ({ attachment: item.file, name: 'image.jpeg' })),
                });
            }
            else if (items.length > 1) {
                yield instagram.publish.album({
                    items: items,
                    caption: `${todayDate} ${SCHOOLNAME} 급식입니다.\n\n#급식 #급식봇 #${SCHOOLNAME} #${String(date.getDate()).padStart(2, "0")}일`,
                });
                console.log("✅ 인스타그램에 앨범이 성공적으로 업로드 되었습니다!");
                webhookClient.send({
                    content: `✅ 인스타그램에 급식 앨범이 업로드되었습니다! **(${todayDate})**`,
                    username: `${SCHOOLNAME} 급식로그`,
                    avatarURL: avatarurl,
                    files: items.map(item => ({ attachment: item.file, name: 'image.jpeg' })),
                });
            }
            // Set flag after successful post
            setFlag();
        }
        catch (loginErr) {
            console.error(`🛑 로그인에 실패했습니다\n${loginErr}`);
            webhookClient.send({
                content: `🛑 로그인에 실패했습니다\n${loginErr}`,
                username: `${SCHOOLNAME} 급식로그`,
                avatarURL: avatarurl,
            });
        }
    }));
});
function scheduleRandomJob(hour, minute) {
    if (cronJob) {
        cronJob.stop();
    }
    if (hour === undefined || minute === undefined) {
        const randomMinute = Math.floor(Math.random() * 180); // Random minute between 0 and 179 (since we want it between 0 and 2:59)
        hour = Math.floor(randomMinute / 60); // Convert to hour range 0-2
        minute = randomMinute % 60; // Get minute part
    }
    const cronExpression = `${minute} ${hour} * * *`;
    cronJob = node_cron_1.default.schedule(cronExpression, () => {
        if (mealNotificationEnabled) {
            webhookClient.send({
                content: "⏰ 급식 전송 시작!",
                username: `${SCHOOLNAME} 급식로그`,
                avatarURL: avatarurl,
            });
            console.log("⏰ 급식 실행됨");
            postToInstagram();
        }
    });
    console.log(`⏰ 급식 전송 스케줄 설정됨: ${cronExpression}`);
    webhookClient.send({
        content: `⏰ 급식 전송 스케줄 설정됨: ${cronExpression}`,
        username: `${SCHOOLNAME} 급식로그`,
        avatarURL: avatarurl,
    });
    // Update the bot's status to show the next scheduled time
    if (client.user) {
        client.user.setActivity(`다음 급식 전송 시간: ${hour}시 ${minute}분`, { type: discord_js_1.ActivityType.Watching });
        console.log(`✅ 상태 메시지 업데이트됨: 다음 급식 전송 시간은 ${hour}시 ${minute}분입니다.`);
    }
}
// Schedule to reset the job at 5 PM
node_cron_1.default.schedule('0 5 * * *', () => {
    console.log("🕔 5시가 되어 급식 전송 시간을 다시 설정합니다.");
    webhookClient.send({
        content: "🕔 5시가 되어 급식 전송 시간을 다시 설정합니다.",
        username: `${SCHOOLNAME} 급식로그`,
        avatarURL: avatarurl,
    });
    scheduleRandomJob(); // 매일 오후 5시에 새로운 급식 전송 시간을 설정합니다.
});
function setFlag() {
    const currentDate = new Date();
    const flag = {
        year: currentDate.getFullYear(),
        month: currentDate.getMonth(),
        date: currentDate.getDate(),
    };
    fs_1.default.writeFileSync(FLAG_FILE, JSON.stringify(flag));
}
function getFlag() {
    if (fs_1.default.existsSync(FLAG_FILE)) {
        const data = fs_1.default.readFileSync(FLAG_FILE, 'utf8');
        const flag = JSON.parse(data);
        const currentDate = new Date();
        return flag.year === currentDate.getFullYear() && flag.month === currentDate.getMonth() && flag.date === currentDate.getDate();
    }
    return false;
}
// Discord bot commands for manual repost, schedule change, notification control, and day settings
client.on("messageCreate", (message) => __awaiter(void 0, void 0, void 0, function* () {
    if (message.author.id === "534214957110394881") {
        if (message.content === "!재전송") {
            console.log("✅ 재전송 명령어 실행됨");
            yield message.reply("급식을 재전송합니다.");
            postToInstagram();
        }
        else if (message.content === "!급식알림 끄기") {
            mealNotificationEnabled = false;
            yield message.reply("🚫 급식 알림이 비활성화되었습니다.");
            console.log("🚫 급식 알림이 비활성화되었습니다.");
            if (client.user) {
                client.user.setActivity("🚫 급식 알림이 비활성화되어 있습니다.", { type: discord_js_1.ActivityType.Watching });
            }
        }
        else if (message.content === "!급식알림 켜기") {
            mealNotificationEnabled = true;
            scheduleRandomJob();
            yield message.reply("✅ 급식 알림이 활성화되었습니다.");
            console.log("✅ 급식 알림이 활성화되었습니다.");
        }
    }
    else if (message.content === "!재전송" || message.content === "!급식알림 끄기" || message.content === "!급식알림 켜기") {
        yield message.reply("⛔ 이 명령어를 사용할 권한이 없습니다.");
    }
}));
// Dokdo setup for administrator commands
const DokdoHandler = new dokdo_1.Client(client, { aliases: ['dokdo', 'dok'], prefix: '!' });
client.on("messageCreate", (message) => __awaiter(void 0, void 0, void 0, function* () {
    if (message.content === 'ping')
        return message.channel.send('Pong');
    DokdoHandler.run(message);
}));
// Discord bot login event
client.once('ready', () => {
    var _a, _b;
    console.log(`✅ 디스코드 봇 로그인 성공: ${(_a = client.user) === null || _a === void 0 ? void 0 : _a.tag}`);
    webhookClient.send({
        content: `✅ 디스코드 봇 로그인 성공: ${(_b = client.user) === null || _b === void 0 ? void 0 : _b.tag}`,
        username: `${SCHOOLNAME} 급식로그`,
        avatarURL: avatarurl,
    });
    // 로그인 이후 첫 스케줄 설정
    scheduleRandomJob();
});
client.login(process.env.DISCORD_BOT_TOKEN);
