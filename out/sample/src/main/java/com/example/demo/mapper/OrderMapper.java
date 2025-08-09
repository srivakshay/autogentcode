package com.example.demo.mapper;

import org.mapstruct.*;
import com.example.demo.entity.OrderEntity;
import com.example.demo.dto.OrderDto;

@Mapper(componentModel = "spring")
public interface OrderMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "priority", source = "totalAmount")
    OrderEntity toEntity(OrderDto orderDto);

    @Mapping(target = "customerName", source = "customerName")
    @Mapping(target = "totalAmount", source = "totalAmount")
    @Mapping(target = "priority", ignore = true)
    OrderDto toDto(OrderEntity orderEntity);

}