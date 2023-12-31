<script setup lang="ts">
import { python } from '@codemirror/lang-python';
import { ElMessage } from 'element-plus';
import { onMounted, reactive, ref, watch } from 'vue';
import { Codemirror } from 'vue-codemirror';

import { request } from '@/utils/request';

import { apis } from '../../utils/apis';
import { generateColor } from '../../utils/color';

import type { FoodDto, Point, SnakeDto } from '@/@types/game';

const DEFAULT_CODE = `
def step(snake, other_snakes, board):
    """
    每一步的决策函数，返回值为 'TURN_LEFT', 'TURN_RIGHT', 'KEEP_STRAIGHT' 之一

    :param snake: 自己的蛇，如 SnakeInfo(
        body_points=[Point(x=0, y=0), Point(x=0, y=1), Point(x=0, y=2)],
        head=Point(x=0, y=0),
        direction='up',  # 'up', 'down', 'left', 'right'
        player=Player(id='2j3lj66x', name='Alice'),
    )
    :param other_snakes: 其他蛇的信息，如 [SnakeInfo(...), SnakeInfo(...)]
    :param board: 地图信息，如 BoardInfo(
        width=20,
        height=20,
        foods=[Food(point=Point(x=1, y=1), color='#ff0000'), Food(...)],
    )
    """

    return 'KEEP_STRAIGHT'
`;

let wsClient: ReturnType<typeof apis.ws.game.createClient>;

const generateRandomName = async (): Promise<string> => {
  const data: { results: Array<{ name: { first: string } }> } =
    await request.get('https://randomuser.me/api/?nat=us');
  return data.results[0].name.first;
};

const playerId = Math.random().toString(36).substr(2);

const canvasRef = ref<HTMLCanvasElement>();

const roomId = ref('room1');
const player = reactive({
  id: playerId,
  name: '',
  score: 0,
});
const snakeColor = generateColor(playerId);
const code = ref(DEFAULT_CODE.trimStart());

const isGaming = ref(false);

const gameButtonText = ref('开始/进入游戏');
const pixelWidth = ref(6);
const pixelHeight = ref(6);

const codemirrorExtensions = ref([python()]);

watch(
  () => code.value,
  (code) => {
    handleUpdateCode(code);
  },
);

onMounted(() => {
  console.info(`Player ID: ${player.id}`);
  console.info(`Snake Color: ${snakeColor}`);

  if (canvasRef.value) {
    pixelWidth.value = canvasRef.value.width / 50;
    pixelHeight.value = canvasRef.value.height / 50;
  }

  (async () => {
    player.name = await generateRandomName();
  })();
});

const drawPixel = (
  options: Point & { color?: string; type?: 'normal' | 'small' },
) => {
  const { color = snakeColor, type = 'normal' } = options;

  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.fillStyle = color;

  if (type === 'small') {
    ctx.fillRect(
      (options.x - 1) * pixelWidth.value + pixelWidth.value / 4,
      (options.y - 1) * pixelHeight.value + pixelHeight.value / 4,
      pixelWidth.value / 2,
      pixelHeight.value / 2,
    );
    return;
  }

  ctx.fillRect(
    (options.x - 1) * pixelWidth.value,
    (options.y - 1) * pixelHeight.value,
    pixelWidth.value,
    pixelHeight.value,
  );
};

const drawSnakes = (snakes: SnakeDto[]) => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (const snake of snakes) {
    for (const point of snake.bodyPoints) {
      drawPixel({ ...point, color: snake.color });
    }
  }
};

const drawFoods = (foods: FoodDto[]) => {
  for (const food of foods) {
    drawPixel({ ...food.point, color: food.color, type: 'small' });
  }
};

/**
 * 开始/结束游戏
 */
const handleToggleGame = () => {
  if (isGaming.value) {
    gameButtonText.value = '开始/进入游戏';
    void handleStopGame();
  } else {
    gameButtonText.value = '结束/退出游戏';
    void handleStartGame();
  }

  isGaming.value = !isGaming.value;
};

/**
 * 开始游戏
 */
const handleStartGame = async () => {
  await apis.game.join({
    roomId: roomId.value,
    player: player,
    snakeColor: snakeColor,
  });

  wsClient = apis.ws.game.createClient({ roomId: roomId.value });
  wsClient.on('message', ({ payload, type }) => {
    if (type === 'update-game') {
      drawSnakes(payload.game.snakes);
      drawFoods(payload.game.board.foods);
      const newScore = payload.game.players.find(
        (player) => player.id === player.id,
      )?.score;
      if (!newScore) return;
      player.score = newScore;
      return;
    }

    if (type === 'code-update-confirm') {
      ElMessage.success('代码已更新');
      return;
    }
  });
  wsClient.on('open', () => {
    handleUpdateCode(code.value);
  });
};

/**
 * 结束游戏
 */
const handleStopGame = async () => {
  wsClient.close();
  await apis.game.quit({ roomId: roomId.value, playerId: player.id });
};

const handleUpdateCode = (code: string) => {
  wsClient.send({
    type: 'update-code',
    payload: {
      playerId: player.id,
      code,
    },
  });
};
</script>

<template>
  <div class="flex h-screen flex-col space-y-1 p-8">
    <div class="w-100 mb-4 flex flex-row justify-between">
      <img
        id="u226_img"
        class="inline h-8 hover:cursor-pointer"
        src="@/assets/images/对战/u226.svg"
        @click="$router.go(-1)" />
      <img
        id="u227_img"
        class="inline h-8 hover:cursor-pointer"
        src="@/assets/images/对战/u227.svg"
        @click="$router.push('/settings')" />
    </div>

    <div class="mb-8 flex flex-row">
      <h1 class="grow text-3xl">Code Snake</h1>
      <span class="text-gray-500"
        >你好，<span :style="{ color: snakeColor }">{{
          player.name
        }}</span></span
      >
    </div>
    <div class="flex flex-row">
      <el-form-item class="mr-3 w-full" label="房间号">
        <el-input
          v-model="roomId"
          type="text"
          placeholder="请输入房间号"></el-input>
      </el-form-item>
      <el-button
        :type="isGaming ? 'danger' : 'info'"
        text
        :style="
          isGaming ? { border: '1px solid red' } : { border: '1px solid gray' }
        "
        @click="handleToggleGame">
        {{ gameButtonText }}
      </el-button>
    </div>

    <div class="flex grow flex-row">
      <!-- 游戏界面 -->
      <div class="flex h-full w-full flex-col items-center p-8">
        <span>当前分数: {{ player.score }}</span>
        <div class="aspect-square w-full border-2">
          <canvas ref="canvasRef" class="h-full w-full"></canvas>
        </div>
      </div>
      <!-- 代码编辑器 -->
      <div class="h-full w-full">
        <codemirror
          v-model="code"
          placeholder="Code goes here..."
          :style="{ width: '100%' }"
          :autofocus="true"
          :indent-with-tab="true"
          :tab-size="4"
          :extensions="codemirrorExtensions" />
      </div>
    </div>
  </div>
</template>
