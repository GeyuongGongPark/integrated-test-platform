import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import login_to_dashborad from "../../login/login_to_dashborad.js";
import { URLS } from '../../url/url_base.js';
import { getFormattedTimestamp } from "../../common/utils.js";

export const options = {
  scenarios: {
    ui: {
      executor: 'shared-iterations',
      options: {
        browser: {
          type: 'firefox',
          defaultViewport: {
            width: 1920,
            height: 1080,
          },
        },
      },
    },
  },
  thresholds: {
    checks: ['rate==1.0'],
  },
};

async function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function () {
  const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
  let page;
  try {
    page = await login_to_dashborad();
      // 임시 저장 리스트 호출
      await page.goto(URLS.CLM.DRAFT);
      let timestamp = getNewTimestamp();
      await page.screenshot({path: `screenshots/${timestamp}_clm.png`});
      // 신규 검토 요청 btn 클릭
      await page.waitForSelector('//button[text()="신규 검토 요청" and not(@disabled)]');
      timestamp = getNewTimestamp();
      await page.screenshot({path: `screenshots/${timestamp}_before_request.png`});
      await page.locator('//button[text()="신규 검토 요청"]').click();
      timestamp = getNewTimestamp();
      await page.screenshot({path: `screenshots/${timestamp}_after_request.png`});
      // 계약 검토 요청 모달 확인 btn 클릭
      await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
      await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
      timestamp = getNewTimestamp();
      await wait(10000);
      await page.screenshot({path: `screenshots/${timestamp}_after_confirm.png`});
      // 계약 검토 요청 작성 시작
      if ( __ENV.CONTRAT_UPLOAD === "use") { // 계약서 업로드 여부 : 사용
        await page.locator('//label[.//div[text()="해지"]]').click();
        await page.waitForSelector('//div[text()="관련 계약 찾아보기"]');
        await page.locator('//div[text()="관련 계약 찾아보기"]').click();
        await page.locator('(//button[text()="선택"])[1]').click(); // 기존 계약 검색 모달 첫번째 계약 선택 
        await page.screenshot({path: `screenshots/${timestamp}_stop.png`});
        // 편집기 사용 여부
        if ( __ENV.EDITER_USE === "use") { // 편집기 사용 여부 : 사용
          await page.locator('//label[.//div[text()="사용"]]').click();
          await page.screenshot({path: `screenshots/screenshot_${timestamp}_after_confirm.png`});
          } else { // 편집기 사용 여부 : 사용 안함
            await page.locator('//label[.//div[text()="사용 안 함"]]').click(); 
            await page.screenshot({path: `screenshots/screenshot_${timestamp}_after_confirm.png`});
        }
        // 계약서 첨부 방식
        if ( __ENV.CONTRAT_TYPE === "file") { // 계약서 첨부 방식 : 파일 업로드
          await page.locator('//label[.//div[text()="파일로 첨부하기"]]').click();
          await page.screenshot({path: `screenshots/${timestamp}_contrat.png`});
          } else { // 계약서 첨부 방식 : My 계약서에서 불러오기
            await page.waitForSelector('//label[.//div[text()="My계약서에서 불러오기"]]')
            await page.locator('//label[.//div[text()="My계약서에서 불러오기"]]').click();
            await page.screenshot({path: `screenshots/${timestamp}_my.png`});
          }
        // 계약서 선택
        if ( __ENV.CONTRAT_SELECT === "file") { // 계약서 첨부 방식 : 파일 업로드
          await page.locator('img[alt="파일 업로드"]').click();
          await page.screenshot({path: `screenshots/${timestamp}_file.png`});
        } else { // 계약서 첨부 방식 : My 계약서에서 불러오기
          await page.waitForSelector('img[alt="불러오기 아이콘"]')
          await page.locator('img[alt="불러오기 아이콘"]').click();
          await page.screenshot({path: `screenshots/${timestamp}_load.png`});
          try {
            await page.waitForSelector('img[src*="loading.gif"]', { state: 'hidden', timeout: 20000 });
          } catch (e) {
            // console.log("로딩 스피너가 사라지지 않음");
            await page.screenshot({path: `screenshots/${timestamp}_loading_timeout.png`});
            // 필요하다면 throw e;로 에러를 다시 던지거나, 그냥 넘어갈 수도 있음
          }
            
          // 문서 불러오기 모달이 나타날 때까지 대기
          await page.waitForSelector('//div[text()="문서 불러오기"]');
            
          // 파일 목록이 로드될 때까지 대기 (로딩 이미지가 사라질 때까지)
          // await page.waitForSelector('img[src*="loading.gif"]', { state: 'hidden' });
            
          // alt="파일"인 문서 선택
          await page.locator('(//img[@alt="파일"]/ancestor::div[contains(@class, "cursor-pointer")])[1]').click();
          await page.screenshot({path: `screenshots/${timestamp}_contract.png`});
          // "선택" 버튼이 보일 때까지 대기 후 클릭
          await page.waitForSelector('//button[text()="선택"]', { state: 'visible', timeout: 5000 });
          await page.locator('//button[text()="선택"]').click();
          await page.screenshot({path: `screenshots/${timestamp}_select.png`});

          // (1) 로딩 스피너가 있다면 사라질 때까지 대기
          try {
            await page.waitForSelector('img[src*="loading.gif"]', { state: 'hidden', timeout: 20000 });
          } catch (e) {}

          // (2) "문서 불러오기" 모달이 닫힐 때까지 대기
          try {
            await page.waitForSelector('//div[text()="문서 불러오기"]', { state: 'hidden', timeout: 10000 });
          } catch (e) {}

          // (3) 약간의 추가 대기 (필요시)
          await wait(500);

        // (4) 이제 계약명 입력, 보안 여부 클릭 등 다음 단계 진행
        await page.locator('input[placeholder="계약명을 입력해 주세요"]').fill(`신규 계약서_${timestamp}`);
        await page.screenshot({path: `screenshots/${timestamp}_name.png`});
        // 보안 여부
        if ( __ENV.SECURITY_TYPE === "all") { // 보안 여부 : 전체 공개
              await page.waitForSelector('//label[.//div[text()="전체 공개"]]', { state: 'visible', timeout: 5000});
              await page.locator('//label[.//div[text()="전체 공개"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_all.png`});
          }
        else if ( __ENV.SECURITY_TYPE === "refer") { // 보안 여부 : 참조인
              await page.locator('//label[.//div[text()="참조인"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_refer.png`});
        }
        else { // 보안 여부 : 비공개
              await page.locator('//label[.//div[text()="비공개"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_hidden.png`});
        }
        // 검토 진행 여부
        if ( __ENV.REVIEW_TYPE === "use") { //검토 진행 여부 : 검토 필요
              await page.locator('//label[.//div[text()="검토 필요"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_review.png`});
        }
        else { // 검토 진행 여부 : 검토 불필요
              await page.locator('//label[.//div[text()="검토 불필요"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_noreview.png`});
        }
        // 검토 마감 기한
        // 계약 검토 요청
        if ( __ENV.APPROVAL_SET === "use") { // 내부 결재선이 있는 경우
              await page.locator('img[alt="결재자 추가하기"]').click();
        }
        else {// 내부 결재선이 없을 경우 노출되는 모달 처리
              await page.locator('//div[text()="계약서 검토 요청"]').click();
              await page.screenshot({path: `screenshots/${timestamp}_creat.png`});
              await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
              // const btn = page.locator('//div[contains(@class, "footer-safe-area")]//button[text()="확인"]')
              // console.log('disabled', await btn.getAttribute('disabled'));
              // console.log('aria-disabled', await btn.getAttribute('aria-disabled'));
              await page.screenshot({path: `screenshots/${timestamp}_asigness.png`});
              await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
              await page.waitForTimeout(10000)
              await page.screenshot({path: `screenshots/${timestamp}_new_contrat.png`});
          }
        }
      }
      else { // 계약서 업로드 여부 : 사용 안함
        // (4) 이제 계약명 입력, 보안 여부 클릭 등 다음 단계 진행
        await page.locator('input[placeholder="계약명을 입력해 주세요"]').fill(`신규 계약서_${timestamp}`);
        await page.screenshot({path: `screenshots/${timestamp}_name.png`});
        // 보안 여부
        if ( __ENV.SECURITY_TYPE === "all") { // 보안 여부 : 전체 공개
              await page.waitForSelector('//label[.//div[text()="전체 공개"]]', { state: 'visible', timeout: 5000});
              await page.locator('//label[.//div[text()="전체 공개"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_all.png`});
          }
        else if ( __ENV.SECURITY_TYPE === "refer") { // 보안 여부 : 참조인
              await page.locator('//label[.//div[text()="참조인"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_refer.png`});
        }
        else { // 보안 여부 : 비공개
              await page.locator('//label[.//div[text()="비공개"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_hidden.png`});
        }
        // 검토 진행 여부
        if ( __ENV.REVIEW_TYPE === "use") { //검토 진행 여부 : 검토 필요
              await page.locator('//label[.//div[text()="검토 필요"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_review.png`});
        }
        else { // 검토 진행 여부 : 검토 불필요
              await page.locator('//label[.//div[text()="검토 불필요"]]').click();
              await page.screenshot({path: `screenshots/${timestamp}_noreview.png`});
        }
        // 검토 마감 기한
        // 계약 검토 요청
        if ( __ENV.APPROVAL_SET === "use") { // 내부 결재선이 있는 경우
              await page.locator('img[alt="결재자 추가하기"]').click();
        }
        else {// 내부 결재선이 없을 경우 노출되는 모달 처리
            await page.locator('//div[text()="계약서 검토 요청"]').click();
            await page.screenshot({path: `screenshots/${timestamp}_creat.png`});
            await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
            // const btn = page.locator('//div[contains(@class, "footer-safe-area")]//button[text()="확인"]')
            // console.log('disabled', await btn.getAttribute('disabled'));
            // console.log('aria-disabled', await btn.getAttribute('aria-disabled'));
            await page.screenshot({path: `screenshots/${timestamp}_asigness.png`});
            await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
            await page.waitForTimeout(10000)
            await page.screenshot({path: `screenshots/${timestamp}_new_contrat.png`});
        }
      }
      return page;
    }
    finally {

        }
    }

    export function handleSummary(data) {
        const timestamp = getFormattedTimestamp().replace(/:/g, '_');  
        return {
              [`Result/clm_draft.stop_summary_${timestamp}.html`]: htmlReport(data),
          };
      }