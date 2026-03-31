interface Props {
  status: string;
}

const FocusStatus = ({ status }: Props) => {
  return <h2>상태: {status}</h2>;
};

export default FocusStatus;