resource "aws_eip" "nat" {
    vpc = true
    tags = {
        Name = "nat"
    } 
}

resource "aws_nat_gateway" "a4danimal_nat" {
    allocation_id = aws_eip.nat.id
    subnet_id = aws_subnet.public-us-east-1a.id
    tags = {
        Name = "a4danimal_nat"
    }
    depends_on = [ aws_internet_gateway.a4danimalvpc-igw ]
}