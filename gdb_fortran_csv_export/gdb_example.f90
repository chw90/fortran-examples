program test

integer :: i
integer, dimension(2) :: res

do i=1,10
   res(1) = i
   res(2) = i**2
!! Set a breakpoint at the following statement
   res(1) = -1
end do

end program test
