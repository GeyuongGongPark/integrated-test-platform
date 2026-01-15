import clm_draftNew from "./clm_draft.new.js";
import clm_draftChange from "./clm_draft.change.js";
import clm_draftStop from "./clm_draft.stop.js";

async function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function clm_draft(page, options = {}) {
  let resultPage = page;
  try {
    if (options.DRAFT_TYPE === "new") {
      resultPage = await clm_draftNew(page, options);
    }
    else if (options.DRAFT_TYPE === "change") {
      resultPage = await clm_draftChange(page, options);
    }
    else if (options.DRAFT_TYPE === "stop") {
      resultPage = await clm_draftStop(page, options);
    }
    else {
      console.log("input options.DRAFT_TYPE");
    }
    return resultPage;
  } catch (error) {
    console.error('clm_draft.js 실행 중 오류:', error);
    throw error;
  }
}
