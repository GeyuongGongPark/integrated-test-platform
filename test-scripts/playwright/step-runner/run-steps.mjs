#!/usr/bin/env node
/**
 * Playwright 단계 실행기 (테스트 케이스 test_steps JSON 실행)
 * 사용: node run-steps.mjs [steps.json 경로]   또는  echo '<json>' | node run-steps.mjs
 * 환경변수: BASE_URL (기본값 http://localhost:3000), STEPS_FILE (경로)
 */

import { chromium } from 'playwright';
import { readFileSync } from 'fs';
import { createInterface } from 'readline';

const BASE_URL = process.env.BASE_URL || process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';
const HEADLESS = process.env.HEADLESS !== 'false';

async function readSteps() {
  const fileArg = process.argv[2] || process.env.STEPS_FILE;
  if (fileArg) {
    const raw = readFileSync(fileArg, 'utf8');
    return JSON.parse(raw);
  }
  const rl = createInterface({ input: process.stdin });
  let input = '';
  for await (const line of rl) input += line;
  if (!input.trim()) {
    console.error('STDERR: steps JSON이 필요합니다. 파일 경로를 인자로 주거나 stdin으로 JSON을 전달하세요.');
    process.exit(2);
  }
  return JSON.parse(input);
}

function resolveUrl(url) {
  if (!url) return BASE_URL;
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  const base = BASE_URL.replace(/\/$/, '');
  return url.startsWith('/') ? `${base}${url}` : `${base}/${url}`;
}

async function runSteps(steps) {
  if (!Array.isArray(steps) || steps.length === 0) {
    console.error('STDERR: steps는 비어 있지 않은 배열이어야 합니다.');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext();
  const page = await context.newPage();
  let lastError = null;

  try {
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      const action = (step.action || '').toLowerCase();

      try {
        if (action === 'navigate' || action === 'goto') {
          const url = resolveUrl(step.url);
          await page.goto(url, { timeout: step.timeout || 30000, waitUntil: step.waitUntil || 'domcontentloaded' });
        } else if (action === 'click') {
          if (step.text) {
            await page.getByText(step.text, step.exact ? { exact: true } : {}).click({ timeout: step.timeout || 10000 });
          } else if (step.selector) {
            await page.locator(step.selector).first().click({ timeout: step.timeout || 10000 });
          } else {
            throw new Error('click 단계에는 selector 또는 text가 필요합니다.');
          }
        } else if (action === 'fill' || action === 'type') {
          const selector = step.selector;
          if (!selector) throw new Error('fill/type 단계에는 selector가 필요합니다.');
          await page.locator(selector).first().fill(step.value ?? '', { timeout: step.timeout || 10000 });
        } else if (action === 'press') {
          const selector = step.selector;
          const key = step.key || step.value;
          if (!key) throw new Error('press 단계에는 key가 필요합니다.');
          if (selector) {
            await page.locator(selector).first().press(key, { timeout: step.timeout || 10000 });
          } else {
            await page.keyboard.press(key);
          }
        } else if (action === 'waitfortimeout' || action === 'wait_for_timeout') {
          const ms = step.timeout ?? step.ms ?? 1000;
          await page.waitForTimeout(ms);
        } else if (action === 'waitforselector' || action === 'wait_for_selector') {
          const selector = step.selector;
          if (!selector) throw new Error('waitForSelector 단계에는 selector가 필요합니다.');
          await page.waitForSelector(selector, { timeout: step.timeout || 10000, state: step.state || 'visible' });
        } else if (action === 'asserttext' || action === 'assert_text') {
          const selector = step.selector;
          const text = step.text ?? step.value;
          if (!text) throw new Error('assertText 단계에는 text가 필요합니다.');
          const locator = selector ? page.locator(selector).first() : page.getByText(text, step.exact ? { exact: true } : {});
          await locator.waitFor({ state: 'visible', timeout: step.timeout || 10000 });
          const content = await locator.textContent();
          if (!content || (step.exact ? content.trim() !== text : !content.includes(text))) {
            throw new Error(`assertText 실패: 기대 "${text}", 실제 "${(content || '').trim().slice(0, 200)}"`);
          }
        } else if (action === 'selectoption') {
          const selector = step.selector;
          const values = step.values || (step.value != null ? [step.value] : []);
          if (!selector || !values.length) throw new Error('selectOption 단계에는 selector와 values가 필요합니다.');
          await page.locator(selector).first().selectOption(values, { timeout: step.timeout || 10000 });
        } else {
          console.error(`STDERR: 알 수 없는 action: ${step.action}`);
          lastError = new Error(`Unknown action: ${step.action}`);
          process.exit(1);
        }
      } catch (err) {
        lastError = err;
        console.error(`STDERR: 단계 ${i + 1} 실패 (action: ${step.action}): ${err.message}`);
        process.exit(1);
      }
    }
  } finally {
    await browser.close();
  }

  if (lastError) process.exit(1);
}

readSteps()
  .then(runSteps)
  .then(() => {
    console.log('STDOUT: 모든 단계 실행 완료.');
    process.exit(0);
  })
  .catch((err) => {
    console.error('STDERR:', err.message);
    process.exit(err.code === 2 ? 2 : 1);
  });
