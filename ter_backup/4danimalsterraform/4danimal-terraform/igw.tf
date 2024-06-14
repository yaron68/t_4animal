resource "aws_internet_gateway" "a4danimalvpc-igw" {
  vpc_id = aws_vpc.a4danimalvpc.id
  tags = {
    Name = "a4danimalvpc-igw"
  }
}