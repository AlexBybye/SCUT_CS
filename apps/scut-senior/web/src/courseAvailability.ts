import type { Course, RetrievalMode } from "./contracts";

export function selectSelectableCourseId(
  courses: readonly Course[],
  currentCourseId: string,
): string {
  const currentCourse = courses.find((course) => course.course_id === currentCourseId);
  if (currentCourse?.selectable) return currentCourse.course_id;
  return courses.find((course) => course.selectable)?.course_id ?? "";
}

export function retrievalAvailabilityLabel(course: Pick<Course, "retrieval_availability">): string {
  switch (course.retrieval_availability) {
    case "fixture":
      return "合成 Fixture";
    case "local_corpus":
      return "已激活本地课程语料";
    case "unavailable":
      return "课程资料未激活或不可用";
  }
}

export function courseAvailabilitySummary(course: Course): string {
  const retrieval = retrievalAvailabilityLabel(course);
  if (!course.retrieval_available) return retrieval;
  if (!course.plugin_loaded) return `${retrieval} · 课程插件未加载`;
  return `${retrieval} · 当前可用`;
}

export function courseOptionLabel(course: Course): string {
  return `${course.display_name}（${courseAvailabilitySummary(course)}）`;
}

export function courseSelectionError(course: Course | undefined): string {
  if (!course) return "所选课程不在当前运行时目录中，请重新选择。";
  if (!course.retrieval_available) return "该课程资料当前未激活或不可用。";
  if (!course.plugin_loaded) return "该课程的插件当前未加载，暂时不能选择。";
  return "该课程当前不可用，请重新选择。";
}

export function courseRuntimeDescription(retrievalMode: RetrievalMode | null): string {
  if (retrievalMode === "fixture") {
    return "当前使用合成 Fixture 检索，仅用于本地链路验证。";
  }
  if (retrievalMode === "local_corpus") {
    return "当前使用已激活的本地课程语料；仅可读取且插件已加载的课程可选。";
  }
  return "正在读取当前检索运行时。";
}
