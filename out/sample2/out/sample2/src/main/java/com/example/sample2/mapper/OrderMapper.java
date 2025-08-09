package com.example.sample2.mapper;

import org.mapstruct.*;
import com.example.sample2.domain.Order;
import com.example.sample2.dto.OrderDTO;

@Mapper(componentModel = "spring")
public interface OrderMapper {
    @Mapping(target = "id", source = "order.id")
    @Mapping(target = "customerName", source = "order.customerName")
    @Mapping(target = "totalAmount", source = "order.totalAmount")
    @Mapping(target = "priority", source = "order.priority")
    OrderDTO toDto(Order order);
}