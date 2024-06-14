resource "aws_subnet" "private-us-east-1a" {
  vpc_id = aws_vpc.a4danimalvpc.id

  cidr_block = "192.168.0.0/19"
  availability_zone = "us-east-1a"
  tags = {
    Name = "private-us-east-1a"
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/4danimal" = "owend"
  }
}
resource "aws_subnet" "public-us-east-1a" {
  vpc_id = aws_vpc.a4danimalvpc.id
  cidr_block = "192.168.64.0/19"
  availability_zone = "us-east-1a"
  tags = {
    Name = "public-us-east-1a"
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/a4danimal" = "owend"
  }
}
resource "aws_subnet" "private-us-east-1b" {
  vpc_id = aws_vpc.a4danimalvpc.id

  cidr_block = "192.168.96.0/19"
  availability_zone = "us-east-1b"
  tags = {
    Name = "private-us-east-1b"
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/4danimal" = "owend"
  }
}
resource "aws_subnet" "public-us-east-1b" {
  vpc_id = aws_vpc.a4danimalvpc.id
  cidr_block = "192.168.128.0/19"
  availability_zone = "us-east-1b"
  tags = {
    Name = "public-us-east-1b"
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/a4danimal" = "owend"
  }
}