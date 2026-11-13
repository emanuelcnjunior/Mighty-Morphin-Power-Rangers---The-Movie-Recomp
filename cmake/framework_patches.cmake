# Keep fixes to the pinned framework reproducible on a fresh checkout.
function(power_rangers_patch_framework framework_root)
  find_package(Git REQUIRED)
  foreach(patch_name snesrecomp-display-memory.patch snesrecomp-select-hd.patch)
  set(patch "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../patches/${patch_name}")
  execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${framework_root}"
    apply --reverse --check "${patch}"
    RESULT_VARIABLE already_applied OUTPUT_QUIET ERROR_QUIET)
  if(already_applied EQUAL 0)
    continue()
  endif()
  execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${framework_root}"
    apply --check "${patch}"
    RESULT_VARIABLE can_apply OUTPUT_QUIET ERROR_VARIABLE patch_error)
  if(NOT can_apply EQUAL 0)
    message(FATAL_ERROR "Cannot apply the Power Rangers display-memory fix. "
      "Check the framework pin and local PPU edits.\n${patch_error}")
  endif()
  execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${framework_root}"
    apply "${patch}" RESULT_VARIABLE applied ERROR_VARIABLE patch_error)
  if(NOT applied EQUAL 0)
    message(FATAL_ERROR "Could not apply framework patch: ${patch_error}")
  endif()
  message(STATUS "Applied Power Rangers framework fix: ${patch_name}")
  endforeach()
endfunction()
