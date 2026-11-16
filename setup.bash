# このファイルは実行せず、source ./setup.bash で読み込む。
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  printf '使い方: source ./setup.bash\n' >&2
  exit 1
fi

if [[ -n "${ROS_DISTRO:-}" && "${ROS_DISTRO}" != jazzy ]]; then
  printf '別の ROS 2 ディストリビューション (%s) が有効です。新しい端末で読み込んでください。\n' "$ROS_DISTRO" >&2
  return 1
fi

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  printf 'ROS 2 Jazzy が /opt/ros/jazzy に見つかりません。\n' >&2
  return 1
fi

source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-waffle}"

_ros2_nav2_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${ROS_LOG_DIR:-}" ]]; then
  export ROS_LOG_DIR="${_ros2_nav2_root}/log/ros"
fi
mkdir -p -- "$ROS_LOG_DIR" || return 1

if [[ -f "${_ros2_nav2_root}/install/local_setup.bash" ]]; then
  source "${_ros2_nav2_root}/install/local_setup.bash"
fi
unset _ros2_nav2_root
